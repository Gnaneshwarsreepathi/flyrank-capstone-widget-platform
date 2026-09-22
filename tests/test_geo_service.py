from unittest.mock import patch

from app.services.geo_service import enrich_ip_address


def test_geo_provider_a_success():
    with patch(
        "app.services.geo_service._call_provider",
        return_value=("Ireland", "Dublin"),
    ) as mock_provider, patch(
        "app.services.geo_service.settings.geo_provider_a_url",
        "https://provider-a.test",
    ), patch(
        "app.services.geo_service.settings.geo_provider_b_url",
        "https://provider-b.test",
    ):
        country, city = enrich_ip_address("8.8.8.8")

    assert country == "Ireland"
    assert city == "Dublin"
    assert mock_provider.call_count == 1

    call = mock_provider.call_args
    assert call.kwargs["provider_url"] == "https://provider-a.test"
    assert call.kwargs["ip_address"] == "8.8.8.8"


def test_geo_provider_a_failure_falls_back_to_provider_b():
    with patch(
        "app.services.geo_service._call_provider",
        side_effect=[
            RuntimeError("Provider A failed"),
            ("Ireland", "Dublin"),
        ],
    ) as mock_provider, patch(
        "app.services.geo_service.settings.geo_provider_a_url",
        "https://provider-a.test",
    ), patch(
        "app.services.geo_service.settings.geo_provider_b_url",
        "https://provider-b.test",
    ):
        country, city = enrich_ip_address("8.8.8.8")

    assert country == "Ireland"
    assert city == "Dublin"
    assert mock_provider.call_count == 2

    first_call = mock_provider.call_args_list[0]
    second_call = mock_provider.call_args_list[1]

    assert first_call.kwargs["provider_url"] == "https://provider-a.test"
    assert second_call.kwargs["provider_url"] == "https://provider-b.test"


def test_geo_both_providers_fail_without_raising():
    with patch(
        "app.services.geo_service._call_provider",
        side_effect=[
            RuntimeError("Provider A failed"),
            RuntimeError("Provider B failed"),
        ],
    ) as mock_provider, patch(
        "app.services.geo_service.settings.geo_provider_a_url",
        "https://provider-a.test",
    ), patch(
        "app.services.geo_service.settings.geo_provider_b_url",
        "https://provider-b.test",
    ):
        country, city = enrich_ip_address("8.8.8.8")

    assert country is None
    assert city is None
    assert mock_provider.call_count == 2


def test_geo_missing_ip_returns_empty_location_without_calling_provider():
    with patch("app.services.geo_service._call_provider") as mock_provider:
        country, city = enrich_ip_address(None)

    assert country is None
    assert city is None
    mock_provider.assert_not_called()
