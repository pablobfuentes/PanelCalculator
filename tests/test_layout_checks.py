"""Layout-check preliminary rules."""

from core.columns import Column
from core.layout_checks import LayoutRules, derive_layout_elements


def test_derive_columns_and_beams():
    columns = [
        Column("C1", 0.0, 0.0, tributary_area_m2=10.0, estimated_load_kn=2.5),
        Column("C2", 5.0, 0.0, tributary_area_m2=10.0, estimated_load_kn=2.5),
        Column("C3", 0.0, 4.0, tributary_area_m2=10.0, estimated_load_kn=2.5),
        Column("C4", 5.0, 4.0, tributary_area_m2=10.0, estimated_load_kn=2.5),
    ]
    elements = derive_layout_elements(columns)
    types = {element.element_type for element in elements}
    assert "column" in types
    assert "beam" in types
    assert len([element for element in elements if element.element_type == "beam"]) == 4


def test_vertical_beams_on_column_lines():
    columns = [
        Column("C1", 0.0, 0.0, tributary_area_m2=10.0, estimated_load_kn=2.5),
        Column("C2", 0.0, 4.0, tributary_area_m2=10.0, estimated_load_kn=2.5),
    ]
    elements = derive_layout_elements(columns)
    vertical = [element for element in elements if element.element_id.startswith("BM-V")]
    assert len(vertical) == 1
    assert vertical[0].span_m == 4.0


def test_beam_span_fail_when_too_long():
    columns = [
        Column("C1", 0.0, 0.0, tributary_area_m2=20.0, estimated_load_kn=5.0),
        Column("C2", 8.0, 0.0, tributary_area_m2=20.0, estimated_load_kn=5.0),
    ]
    rules = LayoutRules(max_recommended_beam_span_m=6.0)
    elements = derive_layout_elements(columns, rules=rules)
    beams = [element for element in elements if element.element_type == "beam"]
    assert len(beams) == 1
    assert beams[0].overall_pass is False
