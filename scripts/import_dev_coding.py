"""Merge codes entered on the phone coding page into analysis/dev_coding.csv.

Usage:
    python import_dev_coding.py <dir>              # -> analysis/dev_coding.csv
    python import_dev_coding.py <dir> --blind      # -> analysis/manual_coding.csv (step 5)

<dir> holds one JSON file per segment, as exported from the coding page's database
(collection "dev": {segment_id, codes: [...], none: bool, notes: str, updatedAt}).
Code columns get 1 for each code applied and 0 otherwise; segments not yet coded on
the page stay empty, so you can see what is missing.
"""
import json
import sys
from pathlib import Path

import pandas as pd

from common import ANALYSIS, MANUAL, code_names, load_codebook

DEV = ANALYSIS / "dev_coding.csv"


def main():
    src = Path(sys.argv[1])
    target = MANUAL if "--blind" in sys.argv else DEV
    codes = code_names(load_codebook())
    dev = pd.read_csv(target, dtype=str).fillna("")
    recs = {}
    for f in src.rglob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        d = d.get("data", d)  # tolerate either a bare body or a {data: ...} wrapper
        sid = d.get("segment_id") or f.stem
        recs[sid] = d

    filled = 0
    for i, row in dev.iterrows():
        r = recs.get(row["segment_id"])
        if not r or not (r.get("codes") or r.get("none")):
            continue
        for c in codes:
            dev.at[i, c] = "1" if c in (r.get("codes") or []) else "0"
        dev.at[i, "notes"] = (r.get("notes") or "").strip()
        filled += 1

    dev.to_csv(target, index=False, encoding="utf-8-sig")
    print(f"{filled}/{len(dev)} segments coded -> {target}")
    missing = dev.loc[dev[codes[0]] == "", "segment_id"].tolist()
    if missing:
        print("not yet coded:", ", ".join(missing))


if __name__ == "__main__":
    main()
