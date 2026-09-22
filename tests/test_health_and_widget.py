from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "flyrank-capstone-api",
    }


def test_widget_embed_is_served():
    response = client.get("/widget/embed.js")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/javascript")
    assert "FlyRank Widget" in response.text


def test_widget_config_cache_headers_and_304():
    first_response = client.get("/widgets/2/config")

    assert first_response.status_code == 200
    assert "ETag" in first_response.headers
    assert (
        first_response.headers["Cache-Control"]
        == "public, max-age=60, must-revalidate"
    )

    etag = first_response.headers["ETag"]

    cached_response = client.get(
        "/widgets/2/config",
        headers={"If-None-Match": etag},
    )

    assert cached_response.status_code == 304
    assert cached_response.headers["ETag"] == etag


def test_widget_config_allows_cross_origin_request():
    response = client.get(
        "/widgets/2/config",
        headers={"Origin": "http://localhost:5500"},
    )

    assert response.status_code == 200
    assert (
        response.headers["access-control-allow-origin"]
        == "http://localhost:5500"
    )
