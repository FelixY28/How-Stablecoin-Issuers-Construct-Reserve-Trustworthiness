"""Step 4: code every segment with an LLM, following the latest codebook.

Usage:
    # Anthropic (default)
    export ANTHROPIC_API_KEY=...
    python scripts/03_llm_code.py --limit 20        # try a few first, read the output
    python scripts/03_llm_code.py                    # then code everything

    # Any OpenAI-compatible API (e.g. DeepSeek)
    export LLM_PROVIDER=openai
    export OPENAI_API_KEY=...
    export OPENAI_BASE_URL=https://api.deepseek.com
    export LLM_MODEL=deepseek-chat
    python scripts/03_llm_code.py

    # Pipeline test without any API (keyword rules, NOT valid research output)
    python scripts/03_llm_code.py --dry-run

Results are cached in data/llm_cache.jsonl, keyed by segment, codebook version and model,
so you can stop and resume at any time. Changing the codebook version or the model starts a
fresh set of codes without deleting the old ones.
Output: data/coded_llm.csv (one 0/1 column per code, plus uncertain and rationale).
"""
import argparse
import json
import os
import re
import time

import pandas as pd
import requests

from common import CODED_LLM, LLM_CACHE, SEGMENTS, code_names, load_codebook

PROVIDER = os.getenv("LLM_PROVIDER", "anthropic").lower()
DEFAULT_MODEL = {"anthropic": "claude-sonnet-5-5", "openai": "gpt-4o-mini"}


def build_system_prompt(cb: dict) -> str:
    lines = [cb["instructions"].strip(), "", "CODEBOOK:"]
    for name, c in cb["codes"].items():
        lines.append(f"\n{name} ({c['label']})")
        lines.append(f"  Definition: {c['definition']}")
        lines.append(f"  Include: {c['include']}")
        lines.append(f"  Exclude: {c['exclude']}")
        for ex in c.get("examples", []):
            lines.append(f"  Example: {ex}")
    lines += ["", cb["output_format"].strip()]
    return "\n".join(lines)


def build_user_prompt(seg: pd.Series) -> str:
    return (f"Company: {seg['company']}\nDocument type: {seg['doc_type']}\nDate: {seg['date']}\n\n"
            f"Paragraph:\n\"\"\"\n{seg['text']}\n\"\"\"")


def call_anthropic(system: str, user: str, model: str) -> str:
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                 "anthropic-version": "2023-06-01", "content-type": "application/json"},
        json={"model": model, "max_tokens": 300, "temperature": 0,
              "system": system, "messages": [{"role": "user", "content": user}]},
        timeout=60)
    r.raise_for_status()
    return "".join(b.get("text", "") for b in r.json()["content"])


def call_openai(system: str, user: str, model: str) -> str:
    base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    if not base.endswith("/v1") and "deepseek" not in base:
        base += "/v1"
    r = requests.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        json={"model": model, "temperature": 0,
              "messages": [{"role": "system", "content": system},
                           {"role": "user", "content": user}]},
        timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


DRY_RULES = {
    "AUTH_STATE": r"\b(GENIUS|OCC|regulat|licen[cs]|charter|federal)",
    "AUTH_PROF": r"\b(audit|attest|Big Four|KPMG|BDO|Deloitte|AICPA|S&P)",
    "AUTH_MARKET": r"\b(redemption|track record|market cap|billion|largest)",
    "AUTH_TECH": r"\b(on-?chain|blockchain|verif|real[- ]time)",
    "AUTH_POLITICAL": r"\b(America|dollar dominance|national|White House)",
    "SELF_ASSURANCE": r"\b(rigorous|world-class|transparen|fully backed)",
    "HEDGE_PENDING": r"\b(designed to|progressing|intends? to|expects? to|plans? to|will )",
    "REBUTTAL": r"\b(disagree|outdated|misleading|FUD)",
    "CONFIRMATION": r"\b(already operating|aligned with|validat)",
}


def dry_run_code(text: str, codes: list[str]) -> dict:
    hits = [c for c in codes if c in DRY_RULES and re.search(DRY_RULES[c], text, re.I)]
    return {"codes": hits, "uncertain": False, "rationale": "DRY RUN keyword rules"}


def parse_json(raw: str, codes: list[str]) -> dict:
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        raise ValueError(f"no JSON in response: {raw[:200]}")
    obj = json.loads(m.group(0))
    valid = [c for c in obj.get("codes", []) if c in codes]
    unknown = [c for c in obj.get("codes", []) if c not in codes]
    return {"codes": valid, "uncertain": bool(obj.get("uncertain", False)) or bool(unknown),
            "rationale": str(obj.get("rationale", ""))
            + (f" [unknown codes dropped: {unknown}]" if unknown else "")}


def load_cache() -> dict:
    cache = {}
    if LLM_CACHE.exists():
        for line in LLM_CACHE.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                cache[(rec["segment_id"], rec["codebook_version"], rec["model"])] = rec
    return cache


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="only code the first N uncoded segments")
    ap.add_argument("--dry-run", action="store_true", help="keyword rules, no API (testing only)")
    ap.add_argument("--sleep", type=float, default=0.5, help="seconds between API calls")
    ap.add_argument("--include-attestation", action="store_true",
                    help="also code attestation reports (codebook v0.2 R5: issuer texts only by default)")
    args = ap.parse_args()

    cb = load_codebook()
    codes = code_names(cb)
    version = cb["version"]
    model = "DRY_RUN" if args.dry_run else os.getenv("LLM_MODEL", DEFAULT_MODEL.get(PROVIDER, ""))
    call = call_anthropic if PROVIDER == "anthropic" else call_openai
    system = build_system_prompt(cb)

    segs = pd.read_csv(SEGMENTS, dtype={"segment_id": str})
    if not args.include_attestation:
        segs = segs[segs["doc_type"] != "attestation"]
    cache = load_cache()
    todo = [s for _, s in segs.iterrows() if (s["segment_id"], version, model) not in cache]
    if args.limit:
        todo = todo[: args.limit]
    print(f"Codebook v{version} ({cb['_path']}), model {model}: {len(todo)} segments to code")

    with open(LLM_CACHE, "a", encoding="utf-8") as f:
        for i, s in enumerate(todo, 1):
            try:
                if args.dry_run:
                    res = dry_run_code(s["text"], codes)
                else:
                    res = parse_json(call(system, build_user_prompt(s), model), codes)
                    time.sleep(args.sleep)
            except Exception as e:  # keep going; failed segments are retried next run
                print(f"  ! {s['segment_id']}: {e}")
                continue
            rec = {"segment_id": s["segment_id"], "codebook_version": version, "model": model, **res}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            cache[(s["segment_id"], version, model)] = rec
            if i % 25 == 0:
                print(f"  {i}/{len(todo)}")

    # build the wide table for this codebook version + model only
    rows = []
    for sid in segs["segment_id"]:
        rec = cache.get((sid, version, model))
        if not rec:
            continue
        row = {"segment_id": sid, **{c: int(c in rec["codes"]) for c in codes},
               "uncertain": int(rec["uncertain"]), "rationale": rec["rationale"],
               "codebook_version": version, "model": model}
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(CODED_LLM, index=False)
    print(f"{len(out)}/{len(segs)} segments coded -> {CODED_LLM}")
    if args.dry_run:
        print("WARNING: dry-run codes are keyword rules for testing the pipeline, not research results.")
    if len(out):
        print("\nShare of segments per code:")
        print(out[codes].mean().sort_values(ascending=False).round(3).to_string())


if __name__ == "__main__":
    main()
