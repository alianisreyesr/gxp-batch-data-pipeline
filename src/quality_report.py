from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any


def render_quality_report(summary: dict[str, Any]) -> str:
    """Render a self-contained, local HTML view of synthetic quality-review signals."""

    def rows(values: dict[str, object]) -> str:
        return "".join(
            f"<tr><td>{escape(str(key))}</td><td>{escape(str(value))}</td></tr>"
            for key, value in values.items()
        )

    queue = "".join(
        "<tr>"
        f"<td>{escape(str(item['batch_id']))}</td>"
        f"<td>{escape(str(item['phase']))}</td>"
        f"<td>{escape(str(item['rule_id']))}</td>"
        f"<td>{escape(str(item['parameter']))}</td>"
        f"<td>{escape(str(item['observed_value']))}</td>"
        f"<td>{escape(str(item['expected_range']))}</td>"
        "</tr>"
        for item in summary["review_queue"]
    )
    total = escape(str(summary["total_oos_flags"]))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Synthetic Batch Quality Review</title>
<style>body{{font-family:system-ui,sans-serif;margin:2rem;color:#172033;background:#f7f9fc}}main{{max-width:1000px;margin:auto}}.card{{background:#fff;border-radius:12px;padding:1.4rem;box-shadow:0 1px 4px #0002;margin:1rem 0}}.metric{{font-size:2.5rem;font-weight:700;color:#b42318}}table{{border-collapse:collapse;width:100%}}th,td{{padding:.65rem;border-bottom:1px solid #dbe2ea;text-align:left}}th{{background:#edf2f7}}small{{color:#52606d}}</style>
</head><body><main>
<h1>Synthetic Batch Quality Review</h1>
<p><small>This portfolio report is generated from fictional synthetic data only. It is not a regulated review, release, or quality decision record.</small></p>
<section class="card"><div class="metric">{total}</div><div>Explainable OOS signals requiring review</div></section>
<section class="card"><h2>Signals by rule</h2><table><tr><th>Rule</th><th>Signals</th></tr>{rows(summary["oos_by_rule"])}</table></section>
<section class="card"><h2>Signals by batch</h2><table><tr><th>Batch</th><th>Signals</th></tr>{rows(summary["oos_by_batch"])}</table></section>
<section class="card"><h2>Review queue</h2><table><tr><th>Batch</th><th>Phase</th><th>Rule</th><th>Parameter</th><th>Observed</th><th>Expected range</th></tr>{queue}</table></section>
</main></body></html>
"""


def write_quality_report(summary: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_quality_report(summary), encoding="utf-8")
