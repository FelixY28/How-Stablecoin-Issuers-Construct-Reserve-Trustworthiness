"""Draw segments for manual coding: a development sample (step 3) and a blind validation sample (step 5).

Usage:
    python 04_sample_manual.py --dev            # step 3: 30 segments for codebook development
    python 04_sample_manual.py                  # step 5: 50 segments for blind validation
    python 04_sample_manual.py --n 30 --seed 7

Outputs:
    --dev  -> analysis/dev_coding.csv     (code these by hand to revise the codebook)
    default -> analysis/manual_coding.csv (code these blind, then run 05_agreement.py)

The validation sample never includes segments from dev_coding.csv: segments you used to
revise the codebook would inflate human-LLM agreement.
Sampling is stratified by company, and within each company proportionally by document group
(issuer texts vs attestation reports), so boilerplate-heavy attestation reports cannot crowd
out issuer texts by chance.

Put 1 in every code column that applies (leave others empty or 0). For the validation sample,
do NOT look at the LLM codes while coding. Use the notes column for doubts.
The script refuses to overwrite a file you have already started filling in.
"""
import argparse

import pandas as pd

from common import ANALYSIS, MANUAL, SEGMENTS, code_names, load_codebook

DEV = ANALYSIS / "dev_coding.csv"


def has_codes(path) -> bool:
    if not path.exists():
        return False
    filled = pd.read_csv(path)
    codes = [c for c in filled.columns if c.isupper()]
    return bool(codes) and filled[codes].notna().any().any()


def stratified(segs: pd.DataFrame, n: int, seed: int, issuer_share: float | None = None) -> pd.DataFrame:
    """Per company: proportional to each doc group's size, or a fixed issuer-text share."""
    segs = segs.assign(doc_group=segs["doc_type"].eq("attestation").map({True: "attestation", False: "issuer"}))
    per_company = max(1, n // segs["company"].nunique())
    parts = []
    for _, comp in segs.groupby("company"):
        shares = comp["doc_group"].value_counts(normalize=True)
        if issuer_share is not None:
            shares = pd.Series({"issuer": issuer_share, "attestation": 1 - issuer_share})
            shares = shares[shares.index.isin(comp["doc_group"].unique())]
        for grp, share in shares.items():
            g = comp[comp["doc_group"] == grp]
            k = min(len(g), max(1, round(per_company * share)))
            parts.append(g.sample(k, random_state=seed))
    return pd.concat(parts).sample(frac=1, random_state=seed)  # shuffle so companies are mixed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev", action="store_true", help="draw the codebook-development sample")
    ap.add_argument("--n", type=int, default=None, help="sample size (default 30 with --dev, else 50)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--issuer-share", type=float, default=None,
                    help="fixed share of issuer texts per company (default: 2/3 with --dev, "
                         "proportional otherwise). Decision 2026-11-22: the codebook targets issuer "
                         "texts, so the dev sample is 10 issuer + 5 attestation segments per company")
    args = ap.parse_args()

    target = DEV if args.dev else MANUAL
    n = args.n or (30 if args.dev else 50)
    if has_codes(target) and not args.overwrite:
        raise SystemExit(f"{target} already contains your codes. Use --overwrite to replace it.")

    codes = code_names(load_codebook())
    segs = pd.read_csv(SEGMENTS)

    if not args.dev:
        if DEV.exists():
            dev_ids = set(pd.read_csv(DEV)["segment_id"])
            segs = segs[~segs["segment_id"].isin(dev_ids)]
            print(f"Excluded {len(dev_ids)} development segments from the validation sample.")
        else:
            print("WARNING: no analysis/dev_coding.csv found; cannot exclude development segments.")

    share = args.issuer_share if args.issuer_share is not None else (2 / 3 if args.dev else None)
    sample = stratified(segs, n, args.seed, share)
    out = sample[["segment_id", "company", "doc_type", "date", "text"]].copy()
    for c in codes:
        out[c] = ""
    out["notes"] = ""
    target.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(target, index=False, encoding="utf-8-sig")  # utf-8-sig opens cleanly in Excel
    print(f"{len(out)} segments written to {target}")
    print(out.groupby(["company", "doc_type"]).size().to_string())
    if args.dev:
        print("Code these by hand, revise the codebook (v0.2) and log changes in codebook/CHANGELOG.md")
    else:
        print("Code them blind (without looking at data/coded_llm.csv), then run 05_agreement.py")


if __name__ == "__main__":
    main()
