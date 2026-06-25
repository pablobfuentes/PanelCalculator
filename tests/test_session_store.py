"""Tests for durable session persistence helpers."""

from ui.session_store import PERSIST_DEFAULTS, WIDGET_TO_PERSIST


def test_every_widget_maps_to_persist_default():
    for widget_key, persist_key in WIDGET_TO_PERSIST.items():
        assert persist_key in PERSIST_DEFAULTS, f"{widget_key} -> {persist_key} missing default"


def test_setup_and_analysis_widgets_are_mapped():
    from ui.session_store import ANALYSIS_WIDGET_KEYS, SETUP_WIDGET_KEYS

    for key in SETUP_WIDGET_KEYS:
        assert key in WIDGET_TO_PERSIST
    for key in ANALYSIS_WIDGET_KEYS:
        assert key in WIDGET_TO_PERSIST
