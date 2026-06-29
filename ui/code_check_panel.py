"""Styled code-check table for Analysis tab."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.code_checks import CodeCheckResult, code_check_rows

_STATUS_COLORS = {
    "PASS": "background-color: #d4edda; color: #155724",
    "WARN": "background-color: #fff3cd; color: #856404",
    "FAIL": "background-color: #f8d7da; color: #721c24",
}


def render_code_check_table(checks: tuple[CodeCheckResult, ...]) -> None:
    if not checks:
        st.info("No code check results.")
        return

    df = pd.DataFrame(code_check_rows(checks))

    def _style_status(row: pd.Series) -> list[str]:
        color = _STATUS_COLORS.get(str(row["Status"]), "")
        return [color] * len(row)

    styled = df.style.apply(_style_status, axis=1)
    st.dataframe(styled, width="stretch", hide_index=True)

    counts = df["Status"].value_counts()
    c1, c2, c3 = st.columns(3)
    c1.metric("PASS", int(counts.get("PASS", 0)))
    c2.metric("WARN", int(counts.get("WARN", 0)))
    c3.metric("FAIL", int(counts.get("FAIL", 0)))

    st.caption(
        "Bending: fb = M/S ≤ 0.66·Fy · Deflection: δ ≤ L/240 · "
        "WARN when utilization > 80%."
    )
