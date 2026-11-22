"""Shared paths and helpers."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
ANALYSIS = ROOT / "analysis"
FIGURES = ANALYSIS / "figures"
CODEBOOK_DIR = ROOT / "codebook"

SOURCES = DATA / "sources.csv"
EVENTS = DATA / "events.csv"
METADATA = DATA / "metadata.csv"
SEGMENTS = DATA / "segments.csv"
LLM_CACHE = DATA / "llm_cache.jsonl"
CODED_LLM = DATA / "coded_llm.csv"
MANUAL = ANALYSIS / "manual_coding.csv"

RAW_EXTS = (".html", ".htm", ".pdf", ".txt")


def latest_codebook_path() -> Path:
    """Return the codebook file with the highest version number."""
    files = sorted(CODEBOOK_DIR.glob("codebook_v*.yaml"),
                   key=lambda p: [int(x) for x in p.stem.split("_v")[1].split(".")])
    if not files:
        raise FileNotFoundError("No codebook_v*.yaml found in codebook/")
    return files[-1]


def load_codebook(path: Path | None = None) -> dict:
    path = path or latest_codebook_path()
    with open(path, encoding="utf-8") as f:
        cb = yaml.safe_load(f)
    cb["_path"] = str(path)
    return cb


def code_names(cb: dict) -> list[str]:
    return list(cb["codes"].keys())


def md_table(df) -> str:
    """Render a DataFrame as a Markdown table without extra dependencies."""
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join("" if v is None else str(v) for v in r.tolist()) + " |")
    return "\n".join(lines)


def find_raw_file(doc_id: str) -> Path | None:
    for ext in RAW_EXTS:
        p = RAW / f"{doc_id}{ext}"
        if p.exists():
            return p
    return None
