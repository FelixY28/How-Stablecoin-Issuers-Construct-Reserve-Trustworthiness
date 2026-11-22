"""Step 6: descriptive analysis of the coded segments.

Usage:
    python scripts/06_analysis.py               # LLM codes everywhere (default)
    python scripts/06_analysis.py --use-human   # replace with manual codes; only after reconciling disagreements

Input : data/segments.csv, data/coded_llm.csv, data/events.csv,
        analysis/manual_coding.csv (read only with --use-human)
Output: analysis/summary_tables.md
        analysis/examples_by_code.md      paragraphs to read closely (step 7)
        analysis/figures/authority_by_company.png
        analysis/figures/codes_by_phase.png

These are descriptive shares from a small corpus. They point you to where to read closely;
they are not statistical tests.
"""
import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from common import (ANALYSIS, CODED_LLM, EVENTS, FIGURES, MANUAL, SEGMENTS,
                    code_names, load_codebook, md_table)

AUTH_CODES = ["AUTH_STATE", "AUTH_PROF", "AUTH_MARKET", "AUTH_TECH", "AUTH_POLITICAL", "SELF_ASSURANCE"]
STANCE_CODES = ["HEDGE_PENDING", "REBUTTAL", "CONFIRMATION"]
COMPANY_COLORS = {"Tether": "#1D9E75", "Circle": "#534AB7"}
CODE_COLORS = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00"]


def assign_phases(df: pd.DataFrame) -> pd.DataFrame:
    ev = pd.read_csv(EVENTS)
    starts = ev[ev["phase_start"].notna()].sort_values("date")
    bounds = [(pd.Timestamp(d), p, lbl) for d, p, lbl in zip(starts["date"], starts["phase_start"], starts["label"])]
    labels = {"P0": "P0 before GENIUS Act"}
    labels.update({p: f"{p} from {d.date()}: {lbl}" for d, p, lbl in bounds})

    def phase(d):
        cur = "P0"
        for start, p, _ in bounds:
            if d >= start:
                cur = p
        return cur

    df["phase"] = pd.to_datetime(df["date"], errors="coerce").apply(lambda d: phase(d) if pd.notna(d) else "unknown")
    return df, labels


def load_coded(codes, use_human=False):
    """LLM codes for every segment (one consistent coder).

    The manual sample is for validation only (05_agreement.py). Pass --use-human to
    overwrite LLM codes with manual codes, but only after you have reconciled the
    disagreements; otherwise two coders with different thresholds get mixed.
    """
    segs = pd.read_csv(SEGMENTS)
    llm = pd.read_csv(CODED_LLM)
    if (llm.get("model") == "DRY_RUN").any():
        print("WARNING: using DRY_RUN codes. Figures are for testing the pipeline only.")
    df = segs.merge(llm[["segment_id", *codes, "uncertain"]], on="segment_id", how="inner")
    df["source"] = "llm"
    if not use_human:
        print("Using LLM codes for all segments; manual codes are kept for validation only.")
        return df
    if MANUAL.exists():
        man = pd.read_csv(MANUAL)
        man[codes] = man[codes].apply(pd.to_numeric, errors="coerce")
        man = man.dropna(subset=codes, how="all")
        if len(man):
            man[codes] = man[codes].fillna(0).astype(int).clip(0, 1)
            df = df.set_index("segment_id")
            overlap = df.index.intersection(man["segment_id"])
            df.loc[overlap, codes] = man.set_index("segment_id").loc[overlap, codes].values
            df.loc[overlap, "source"] = "human"
            df = df.reset_index()
            print(f"Using your manual codes for {len(overlap)} segments.")
    return df


def share_table(df, by, cols):
    g = df.groupby(by)
    t = g[cols].mean().round(3)
    t.insert(0, "n_segments", g.size())
    return t.reset_index()


def fig_authority(issuer):
    t = issuer.groupby("company")[AUTH_CODES].mean()
    companies = [c for c in COMPANY_COLORS if c in t.index] + [c for c in t.index if c not in COMPANY_COLORS]
    x = range(len(AUTH_CODES))
    w = 0.8 / max(1, len(companies))
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for i, comp in enumerate(companies):
        ax.bar([xi + i * w for xi in x], t.loc[comp, AUTH_CODES].values, width=w,
               label=f"{comp} (n={int((issuer['company'] == comp).sum())})",
               color=COMPANY_COLORS.get(comp, "#888780"))
    ax.set_xticks([xi + w * (len(companies) - 1) / 2 for xi in x])
    ax.set_xticklabels([c.replace("_", "\n") for c in AUTH_CODES], fontsize=9)
    ax.set_ylabel("Share of paragraphs with code")
    ax.set_title("Sources of authority invoked in issuer texts", loc="left", fontsize=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "authority_by_company.png", dpi=200)
    plt.close(fig)


def fig_phases(issuer, phase_order):
    plot_codes = ["AUTH_STATE", "AUTH_PROF", *STANCE_CODES]
    companies = sorted(issuer["company"].unique())
    shared = [p for p in phase_order if p in issuer["phase"].unique()]  # same x-axis for every company
    fig, axes = plt.subplots(1, len(companies), figsize=(5.2 * len(companies), 4.2), sharey=True, squeeze=False)
    for ax, comp in zip(axes[0], companies):
        sub = issuer[issuer["company"] == comp]
        t = sub.groupby("phase")[plot_codes].mean().reindex(shared)
        n = sub.groupby("phase").size().reindex(shared).fillna(0)
        for code, color in zip(plot_codes, CODE_COLORS):
            ax.plot(range(len(t)), t[code].values, marker="o", label=code, color=color, linewidth=1.8)
        ax.set_xticks(range(len(t)))
        ax.set_xticklabels([f"{p}\n(n={int(k)})" for p, k in zip(t.index, n)], fontsize=9)
        ax.set_title(comp, loc="left", fontsize=12)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.25)
    axes[0][0].set_ylabel("Share of paragraphs with code")
    axes[0][-1].legend(frameon=False, fontsize=8, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.suptitle("Tether: authority and stance codes across event phases (official texts)", x=0.01, ha="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIGURES / "codes_by_phase.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def examples(df, codes, k=4):
    out = ["# Paragraphs for close reading", "",
           "Up to four paragraphs per code and company. Human-coded paragraphs are listed first.", ""]
    for c in codes:
        out.append(f"## {c}")
        for comp, sub in df[df[c] == 1].groupby("company"):
            out.append(f"### {comp}")
            sub = sub.sort_values(["source", "date"], ascending=[True, True]).head(k)
            for _, r in sub.iterrows():
                out.append(f"- **{r['segment_id']}** ({r['date']}, {r['doc_type']}, {r['source']}): {r['text']}")
        out.append("")
    return "\n".join(out)


def main():
    codes = code_names(load_codebook())
    FIGURES.mkdir(parents=True, exist_ok=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--use-human", action="store_true",
                    help="replace LLM codes with manual codes (only after reconciling disagreements)")
    args = ap.parse_args()
    df = load_coded(codes, use_human=args.use_human)
    df, phase_labels = assign_phases(df)
    phase_order = ["P0", *[p for p in phase_labels if p != "P0"]]

    # CEO posts on X are reported separately, never pooled with official issuer texts
    # (decision 2026-11-22: the CEO's bio says "Views are my own"; see analysis/corpus_decisions.md)
    issuer = df[~df["doc_type"].isin(["attestation", "x_post"])]
    xposts = df[df["doc_type"] == "x_post"]
    attest = df[df["doc_type"] == "attestation"]

    md = ["# Summary tables", "",
          f"Coded paragraphs: {len(df)} (official issuer texts {len(issuer)}, CEO posts on X {len(xposts)}, "
          f"attestation reports {len(attest)}). Codes: {'human where coded, LLM elsewhere' if args.use_human else 'LLM for every segment'}.",
          "Values are the share of paragraphs carrying each code.", "",
          "## Phases", *[f"- {v}" for v in phase_labels.values()], "",
          "## Official issuer texts by company", md_table(share_table(issuer, "company", codes)), "",
          "## Tether official texts by phase", "Phases are drawn from Tether's event timeline; Circle's issuer texts all fall after E3, so Circle is not phased (decision D6).",
          md_table(share_table(issuer[issuer["company"] == "Tether"], "phase", codes)), ""]
    if len(xposts):
        md += ["## CEO posts on X (reported separately)", md_table(share_table(xposts, ["company", "doc_id"], codes)), ""]
    if len(attest):
        md += ["## Attestation reports by company", md_table(share_table(attest, "company", codes)), ""]
    (ANALYSIS / "summary_tables.md").write_text("\n".join(md), encoding="utf-8")
    (ANALYSIS / "examples_by_code.md").write_text(examples(df, codes), encoding="utf-8")

    if len(issuer):
        fig_authority(issuer)
        fig_phases(issuer[issuer["company"] == "Tether"], phase_order)
    print("Wrote analysis/summary_tables.md, analysis/examples_by_code.md and two figures in analysis/figures/")
    print("Next: read examples_by_code.md closely and write analytic memos (step 7).")


if __name__ == "__main__":
    main()
