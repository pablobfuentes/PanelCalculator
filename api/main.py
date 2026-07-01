"""SolarForge FastAPI application — HTML frontend + JSON layout API."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from api.catalog import default_catalog
from api.layout_check_service import compute_layout_check
from api.layout_service import compute_layout
from api.schemas import (
    LayoutCheckRequest,
    LayoutCheckResponse,
    LayoutRequest,
    LayoutResponse,
    PanelTypeOut,
)

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"

app = FastAPI(title="SolarForge", version="1.0.0")

app.mount("/static", StaticFiles(directory=WEB), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB / "index.html")


@app.get("/layout")
def layout_page() -> FileResponse:
    return FileResponse(WEB / "layout.html")


@app.get("/structure")
def structure_redirect() -> RedirectResponse:
    return RedirectResponse(url="/layout", status_code=302)


@app.get("/api/catalog", response_model=list[PanelTypeOut])
def get_catalog() -> list[PanelTypeOut]:
    return [
        PanelTypeOut(
            key=p.key,
            name=p.name,
            length=p.length,
            width=p.width,
            weight=p.weight,
            watt_peak=p.watt_peak,
            color=p.color,
            tilt_angle=p.tilt_angle,
        )
        for p in default_catalog()
    ]


@app.post("/api/layout-check", response_model=LayoutCheckResponse)
def post_layout_check(req: LayoutCheckRequest) -> LayoutCheckResponse:
    try:
        return compute_layout_check(req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/structure", response_model=LayoutCheckResponse)
def post_structure_alias(req: LayoutCheckRequest) -> LayoutCheckResponse:
    """Backward-compatible alias for layout-check."""
    return post_layout_check(req)


@app.post("/api/layout", response_model=LayoutResponse)
def post_layout(req: LayoutRequest) -> LayoutResponse:
    try:
        return compute_layout(req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
