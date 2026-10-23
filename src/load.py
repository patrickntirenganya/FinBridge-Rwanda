"""Portable loaders for the NISR microdata.

Expected layout (data/raw is gitignored and never committed):
    data/raw/FinScope_2024_Rwanda.dta      # catalog/120
    data/raw/Microdata.zip                 # catalog/123 (AHS 2024), auto-extracted
"""
from __future__ import annotations
import zipfile
from functools import lru_cache
from pathlib import Path
import pyreadstat

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
FINSCOPE_FILE = RAW / "FinScope_2024_Rwanda.dta"
AHS_ZIP = RAW / "Microdata.zip"
AHS_DIR = RAW / "ahs"

MISSING_HELP = (
    "Raw microdata not found. Download from the NISR Microdata Portal "
    "(https://microdata.statistics.gov.rw) and place:\n"
    "  FinScope 2024 (catalog/120) -> data/raw/FinScope_2024_Rwanda.dta\n"
    "  AHS 2024 (catalog/123)      -> data/raw/Microdata.zip"
)


def _read(path: Path):
    try:
        return pyreadstat.read_dta(str(path))
    except UnicodeDecodeError:          # AHS Section 1 is Latin-1 encoded
        return pyreadstat.read_dta(str(path), encoding="latin1")


@lru_cache(maxsize=1)
def finscope():
    """Return (DataFrame, metadata) for FinScope 2024."""
    if not FINSCOPE_FILE.exists():
        raise FileNotFoundError(MISSING_HELP)
    return _read(FINSCOPE_FILE)


def _ahs_dir() -> Path:
    if not any(AHS_DIR.rglob("*.dta")):
        if not AHS_ZIP.exists():
            raise FileNotFoundError(MISSING_HELP)
        with zipfile.ZipFile(AHS_ZIP) as z:
            z.extractall(AHS_DIR)
    return AHS_DIR


@lru_cache(maxsize=None)
def ahs(module: str):
    """Return (DataFrame, metadata) for one AHS file, matched by name fragment.

    Examples: ahs("Section0"), ahs("Credits"), ahs("Saving"), ahs("Section1_"),
    ahs("Section2"), ahs("Section6").
    """
    files = sorted(_ahs_dir().rglob("*.dta"))
    hits = [f for f in files if module in f.name]
    if len(hits) != 1:
        raise ValueError(f"'{module}' matched {len(hits)} AHS files: {[h.name for h in hits]}")
    return _read(hits[0])


def labels(meta, var: str) -> dict:
    """Value labels for a variable (empty dict if none)."""
    return meta.value_labels.get(meta.variable_to_label.get(var), {}) or {}
