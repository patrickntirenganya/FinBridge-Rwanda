"""Peer reference for farmers: AHS 2024 yield bands and input use.

The ONLY module in src/ or ui/ allowed to read data/aggregates, and only the two files below.
A band is computed on the fly, shown on screen, and never stored: nothing here is imported by
records.py, share.py or the report/export code (tests/test_app.py enforces both).
"""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path

_AGG = Path(__file__).resolve().parents[1] / "data" / "aggregates"
YIELD_FILE = "yield_benchmarks.json"
INPUT_FILE = "input_use.json"

SOURCE_LINE = "AHS 2024, plots of the same crop and season, for guidance only"
SEED_DENOMINATOR = "seasonal-crop plots where seed type was recorded"
BELOW, TYPICAL, ABOVE = "below", "typical", "above"
INTERCROP_HINT = "Most maize and bean plots are mixed with other crops. Enter the share of the plot this crop covers."


@lru_cache(maxsize=None)
def _load(name: str) -> dict:
    return json.loads((_AGG / name).read_text())


def crops_for(season: str) -> list[str]:
    return sorted({b["crop"] for b in _load(YIELD_FILE)["benchmarks"] if b["season"] == season})


def band(crop: str, season: str, harvest_kg: float, plot_m2: float, share_pct: float = 100) -> dict | None:
    """Where one harvest sits among similar plots. Returns None when there is no benchmark or input is unusable."""
    if harvest_kg is None or plot_m2 is None or harvest_kg <= 0 or plot_m2 <= 0:
        return None
    ref = next((b for b in _load(YIELD_FILE)["benchmarks"] if b["crop"] == crop and b["season"] == season), None)
    if ref is None:
        return None
    share = min(max(share_pct or 100, 1), 100)
    y = harvest_kg / (plot_m2 / 10000 * share / 100)
    where = BELOW if y < ref["p25"] else ABOVE if y > ref["p75"] else TYPICAL
    return dict(band=where, yield_kg_ha=round(y), p25=ref["p25"], p50=ref["p50"], p75=ref["p75"], n=ref["n"],
                source=SOURCE_LINE)


def input_share(indicator: str, district: str | None = None) -> dict | None:
    """Weighted share of plots using an input, for a district if reported (n >= 30), else Rwanda."""
    d = _load(INPUT_FILE)
    row = (d["districts"].get(district) or {}).get(indicator) if district else None
    scope = district if row else "Rwanda"
    row = row or d["national"].get(indicator)
    return None if row is None else dict(row, scope=scope, source=SOURCE_LINE)
