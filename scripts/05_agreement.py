"""Step 5b: compare your manual codes with the LLM codes.

Usage:
    python scripts/05_agreement.py

Input : analysis/manual_coding.csv (filled in by you), data/coded_llm.csv
Output: analysis/agreement.md        per-code agreement and Cohen's kappa
        analysis/disagreements.csv   every segment-code pair where you and the LLM differ

Note: with one human coder this measures human-LLM agreement, not inter-coder reliability.
Say so in the memo.
"""
import pandas as pd
from sklearn.metrics import cohen_kappa_score

from common import ANALYSIS, CODED_LLM, MANUAL, code_names, load_codebook, md_table


def interpret(k):
    if pd.isna(k):
        return "n/a"
    for cut, label in [(0.8, "almost perfect"), (0.6, "substantial"), (0.4, "moderate"),
                       (0.2, "fair"), (0.0, "slight")]:
        if k > cut:
            return label
    return "poor"


def main():
    codes = code_names(load_codebook())
    human = pd.read_csv(MANUAL)
    llm = pd.read_csv(CODED_LLM)
    human[codes] = human[codes].apply(pd.to_numeric, errors="coerce").fillna(0).astype(int).clip(0, 1)

    m = human.merge(llm[["segment_id", *codes, "rationale"]], on="segment_id",
                    suffixes=("_human", "_llm"))
    if m.empty:
        raise SystemExit("No overlap between manual_coding.csv and coded_llm.csv. Run 03_llm_code.py first.")

    rows, dis = [], []
    for c in codes:
        h, l = m[f"{c}_human"], m[f"{c}_llm"]
        agree = (h == l).mean()
        kappa = cohen_kappa_score(h, l) if h.nunique() > 1 or l.nunique() > 1 else float("nan")
        rows.append({"code": c, "n": len(m), "human_yes": int(h.sum()), "llm_yes": int(l.sum()),
                     "agreement": round(agree, 3), "kappa": round(kappa, 3) if pd.notna(kappa) else None,
                     "interpretation": interpret(kappa)})
        for _, r in m[h != l].iterrows():
            dis.append({"segment_id": r["segment_id"], "code": c,
                        "human": int(r[f"{c}_human"]), "llm": int(r[f"{c}_llm"]),
                        "llm_rationale": r["rationale"], "text": r["text"]})

    table = pd.DataFrame(rows)
    pd.DataFrame(dis).to_csv(ANALYSIS / "disagreements.csv", index=False, encoding="utf-8-sig")

    md = ["# Human-LLM agreement", "",
          f"Segments compared: {len(m)}. One human coder versus the LLM; this is not inter-coder reliability.", "",
          "Kappa guide (Landis & Koch): >0.8 almost perfect, >0.6 substantial, >0.4 moderate.",
          "Kappa is unstable when a code is rare in the sample; read it together with the counts.", "",
          md_table(table), "",
          "## Next steps",
          "1. Read analysis/disagreements.csv code by code.",
          "2. For each disagreement decide: was the LLM wrong, were you wrong, or is the definition unclear?",
          "3. Unclear definitions -> revise the codebook, log it in codebook/CHANGELOG.md, save as a new version, rerun 03."]
    (ANALYSIS / "agreement.md").write_text("\n".join(md), encoding="utf-8")
    print(table.to_string(index=False))
    print(f"\n{len(dis)} disagreements -> analysis/disagreements.csv; summary -> analysis/agreement.md")


if __name__ == "__main__":
    main()
