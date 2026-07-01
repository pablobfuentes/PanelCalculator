"""API layout endpoint tests."""

from fastapi.testclient import TestClient

from api.main import app
from api.schemas import LayoutRequest

client = TestClient(app)


def test_get_catalog():
    res = client.get("/api/catalog")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 2
    assert data[0]["key"] == "A"


def test_post_layout_default():
    res = client.post("/api/layout", json=LayoutRequest().model_dump())
    assert res.status_code == 200
    body = res.json()
    assert body["stats"]["panel_count"] > 0
    assert len(body["panels"]) > 0
    assert len(body["alleys"]) > 0
    assert body["max_area"]["w"] == 12.0


def test_post_layout_custom_panel():
    res = client.post(
        "/api/layout",
        json={
            "panel_key": "C",
            "panel": {
                "key": "C",
                "name": "Panel C",
                "length": 2.0,
                "width": 1.0,
                "weight": 20.0,
                "watt_peak": 400.0,
                "color": "#E74C3C",
                "tilt_angle": 10.0,
            },
            "max_area_x": 12.0,
            "max_area_y": 8.0,
        },
    )
    assert res.status_code == 200
    assert res.json()["panel"]["key"] == "C"


def test_index_html():
    res = client.get("/")
    assert res.status_code == 200
    assert "SolarForge" in res.text
