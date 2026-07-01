"""API layout-check endpoint tests."""

from fastapi.testclient import TestClient

from api.main import app
from api.schemas import LayoutCheckRequest, LayoutRequest

client = TestClient(app)


def _sample_snapshot():
    layout = client.post("/api/layout", json=LayoutRequest().model_dump()).json()
    return layout["snapshot"]


def test_layout_page():
    res = client.get("/layout")
    assert res.status_code == 200
    assert "Layout" in res.text
    assert "layout.js" in res.text


def test_structure_redirects_to_layout():
    res = client.get("/structure", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["location"] == "/layout"


def test_post_layout_check_default():
    snap = _sample_snapshot()
    req = LayoutCheckRequest(snapshot=snap)
    res = client.post("/api/layout-check", json=req.model_dump())
    assert res.status_code == 200
    body = res.json()
    assert body["metrics"]["partition_ok"] is True
    assert body["metrics"]["element_count"] > 0
    assert len(body["elements"]) == body["metrics"]["element_count"]
    assert "fea" not in body
    assert "code_checks" not in body
    assert "data" in body["figure"]
    beam_types = [element for element in body["elements"] if element["element_type"] == "beam"]
    assert len(beam_types) > 0


def test_layout_check_alias_route():
    snap = _sample_snapshot()
    res = client.post("/api/structure", json={"snapshot": snap})
    assert res.status_code == 200
    assert "elements" in res.json()
