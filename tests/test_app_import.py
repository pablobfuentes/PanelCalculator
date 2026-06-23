"""Import smoke test — catches Streamlit startup import errors."""

import importlib.util
import os
from pathlib import Path


def test_app_module_imports():
    os.environ["PANEL_CALCULATOR_SKIP_RELOAD"] = "1"
    app_path = Path(__file__).resolve().parent.parent / "app.py"
    spec = importlib.util.spec_from_file_location("panel_calculator_app", app_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def test_layout_bbox_import():
    from core.layout import layout_bbox

    assert callable(layout_bbox)
