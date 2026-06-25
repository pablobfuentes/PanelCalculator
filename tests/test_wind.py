"""Tests for wind input helpers."""

import pytest

from core.wind import EXPOSURE_DESCRIPTIONS, exposure_label


@pytest.mark.parametrize("category", ["A", "B", "C", "D"])
def test_exposure_label_includes_category_and_description(category: str):
    label = exposure_label(category)
    assert label.startswith(f"{category} —")
    assert EXPOSURE_DESCRIPTIONS[category] in label


def test_exposure_label_rejects_unknown_category():
    with pytest.raises(ValueError):
        exposure_label("Z")
