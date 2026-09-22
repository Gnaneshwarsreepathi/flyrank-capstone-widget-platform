import httpx

from app.core.config import settings


def _extract_location(data: dict) -> tuple[str | None, str | None]:
    """
    Extract country and city from a provider response.

    Supports common response field names so the service can work
    with different geo-IP providers.
    """
    country = (
        data.get("country")
        or data.get("country_name")
        or data.get("countryCode")
    )

    city = (
        data.get("city")
        or data.get("city_name")
    )

    return country, city


def _call_provider(
    provider_url: str,
    api_key: str | None,
    ip_address: str,
) -> tuple[str | None, str | None]:
    if not provider_url:
        raise RuntimeError("Geo provider URL is not configured")

    headers = {}

    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        headers["X-API-Key"] = api_key

    response = httpx.get(
        provider_url,
        params={"ip": ip_address},
        headers=headers,
        timeout=2.0,
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, dict):
        raise RuntimeError("Invalid geo provider response")

    country, city = _extract_location(data)

    if not country and not city:
        raise RuntimeError("Geo provider returned no location data")

    return country, city


def enrich_ip_address(
    ip_address: str | None,
) -> tuple[str | None, str | None]:
    """
    Try Geo Provider A first.

    If Provider A fails, try Provider B.

    If both providers fail, return empty location data so
    submission storage can continue normally.
    """
    if not ip_address:
        return None, None

    try:
        return _call_provider(
            provider_url=settings.geo_provider_a_url,
            api_key=settings.geo_provider_a_api_key,
            ip_address=ip_address,
        )
    except Exception:
        pass

    try:
        return _call_provider(
            provider_url=settings.geo_provider_b_url,
            api_key=settings.geo_provider_b_api_key,
            ip_address=ip_address,
        )
    except Exception:
        pass

    return None, None