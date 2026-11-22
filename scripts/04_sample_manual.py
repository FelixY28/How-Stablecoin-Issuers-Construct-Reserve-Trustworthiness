"""Step 5a: draw a sample of segments for blind manual coding.

Usage:
    python scripts/04_sample_manual.py            # 50 segments, stratified by company
    python scripts/04_sample_manual.py --n 30 --seed 7

Output: analysis/manual_coding.csv
Open it in Excel or Numbers and put 1 in every code column that applies (leave others empty
or 0). Do NOT look at the LLM codes while doing this: blind coding is what makes the
comparison meaningful. Use the notes column for doubts; they feed the codebook changelog.
The script refuses to overwrite a file you have already started filling in.
"""
import argparse

import pandas as pd

from common import MANUAL, SEGMENTS, code_names, load_codebook


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    if MANUAL.exists() and not args.overwrite:
        filled = pd.read_csv(MANUAL)
        codes = [c for c in filled.columns if c.isupper()]
        if filled[codes].notna().any().any():
            raise SystemExit(f"{MANUAL} already contains your codes. Use --overwrite to replace it.")

    codes = code_names(load_codebook())
    segs = pd.read_csv(SEGMENTS)
    per_company = max(1, args.n // segs["company"].nunique())
    parts = [g.sample(min(len(g), per_company), random_state=args.seed)
             for _, g in segs.groupby("company")]
    sample = pd.concat(parts).sample(frac=1, random_state=args.seed)  # shuffle so companies are mixed

    out = sample[["segment_id", "company", "doc_type", "date", "text"]].copy()
    for c in codes:
        out[c] = ""
    out["notes"] = ""
    MANUAL.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(MANUAL, index=False, encoding="utf-8-sig")  # utf-8-sig opens cleanly in Excel
    print(f"{len(out)} segments written to {MANUAL}")
    print("Code them blind (without looking at data/coded_llm.csv), then run 05_agreement.py")


if __name__ == "__main__":
    main()
