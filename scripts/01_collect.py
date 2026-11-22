"""Step 1: download the documents listed in data/sources.csv and record metadata.

Usage:
    python scripts/01_collect.py            # download missing files
    python scripts/01_collect.py --force    # re-download everything

Files are saved as data/raw/<doc_id>.<html|pdf>.
If a site blocks the download, save the page yourself (browser: Save Page As, or copy the
text into a .txt file) using the same name, e.g. data/raw/T-PR-20251126.txt, and rerun.
The script never overwrites a file you saved by hand unless you pass --force.
"""
import argparse
import hashlib
import time
from datetime import datetime, timezone

import pandas as pd
import requests

from common import METADATA, RAW, SOURCES, find_raw_file

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
    "Accept-Language": "en-US,en;q=0.9",
}


def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def guess_ext(url: str, content_type: str) -> str:
    if "pdf" in content_type.lower() or url.lower().split("?")[0].endswith(".pdf"):
        return ".pdf"
    return ".html"


def download(doc_id: str, url: str) -> tuple[str, str]:
    """Return (status, message)."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
    except requests.RequestException as e:
        return "failed", f"request error: {e}"
    if r.status_code != 200:
        return "failed", f"HTTP {r.status_code}"
    ext = guess_ext(url, r.headers.get("Content-Type", ""))
    if ext == ".html" and len(r.text) < 2000:
        return "failed", "page too short (possibly blocked or a JavaScript-only page)"
    (RAW / f"{doc_id}{ext}").write_bytes(r.content)
    return "downloaded", ext


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    src = pd.read_csv(SOURCES, dtype=str).fillna("")
    rows, failures = [], []

    for _, s in src.iterrows():
        doc_id, url = s["doc_id"], s["url"].strip()
        existing = find_raw_file(doc_id)
        status, msg = "", ""

        if existing and not args.force:
            status, msg = "present", "file already in data/raw"
        elif url:
            status, msg = download(doc_id, url)
            time.sleep(1.5)  # be polite to servers
        else:
            status, msg = "missing", "no url and no file in data/raw"

        path = find_raw_file(doc_id)
        if status in ("failed", "missing"):
            failures.append((doc_id, msg, s["notes"]))
        rows.append({
            **s.to_dict(),
            "file": path.name if path else "",
            "sha256": sha256(path) if path else "",
            "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds") if path else "",
            "status": status,
            "status_msg": msg,
        })
        print(f"[{status:10}] {doc_id}  {msg}")

    pd.DataFrame(rows).to_csv(METADATA, index=False)
    print(f"\nMetadata written to {METADATA}")
    if failures:
        print("\nNeeds your attention (save manually as data/raw/<doc_id>.html/.pdf/.txt):")
        for doc_id, msg, notes in failures:
            print(f"  - {doc_id}: {msg}" + (f"  | hint: {notes}" if notes else ""))


if __name__ == "__main__":
    main()
