"""Step 2: extract text from raw files, clean it, and split it into paragraphs.

Usage:
    python scripts/02_clean_segment.py

Input : data/metadata.csv and data/raw/*
Output: data/segments.csv (one row per paragraph)

Handles .html, .pdf and .txt. For PDFs it removes header/footer lines that repeat on most
pages and rebuilds paragraphs from line breaks. Scanned PDFs (almost no extractable text)
are reported so you can OCR them or skip them.
"""
import re
from collections import Counter

import pandas as pd
import pdfplumber
from bs4 import BeautifulSoup

from common import METADATA, SEGMENTS, find_raw_file

MIN_CHARS = 40  # drop very short fragments (menus, captions, page numbers)

BOILERPLATE = re.compile(
    r"(cookie|subscribe|newsletter|all rights reserved|privacy policy|terms of (use|service)|"
    r"follow us|share this|sign up|read more|back to top|©)", re.I)


def norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


# ---------- HTML ----------
def html_paragraphs(path) -> list[str]:
    soup = BeautifulSoup(path.read_bytes(), "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "aside", "form", "svg"]):
        tag.decompose()
    # first container that actually holds text (some sites ship an empty <article>)
    candidates = [soup.find("article"), soup.find("main"), soup.body, soup]
    root = next(c for c in candidates if c is not None and len(c.get_text(strip=True)) > 200 or c is soup)
    paras = []
    for el in root.find_all(["p", "li", "h2", "h3", "blockquote"]):
        # skip elements nested in another collected element (e.g. <p> inside <li>)
        if el.find_parent(["li", "blockquote"]) and el.name == "p":
            continue
        t = norm_space(el.get_text(" "))
        if t:
            paras.append(t)
    return paras


# ---------- PDF ----------
def _line_key(line: str) -> str:
    """Normalise a line for header/footer detection (ignore digits such as page numbers)."""
    return re.sub(r"\d+", "#", norm_space(line)).lower()


def is_heading(line: str) -> bool:
    """Short title-case line without final punctuation, e.g. 'Independent Auditors' Report'."""
    words = line.split()
    if not (1 <= len(words) <= 12) or line.endswith((".", ",", ";", ":")):
        return False
    caps = sum(w[0].isupper() for w in words if w[0].isalpha())
    return caps >= 0.6 * sum(w[0].isalpha() for w in words)


def parse_pages(spec: str, n: int) -> list[int]:
    """'2-5' or '2-5,9' (1-based, inclusive) -> 0-based page indices. Empty = all pages."""
    if not spec.strip():
        return list(range(n))
    idx = []
    for part in spec.split(","):
        a, _, b = part.strip().partition("-")
        idx += range(int(a) - 1, int(b or a))
    return [i for i in idx if 0 <= i < n]


def pdf_paragraphs(path, page_spec: str = "") -> tuple[list[str], int]:
    with pdfplumber.open(path) as pdf:
        # use_text_flow follows the PDF's content order, which keeps multi-column layouts readable
        pages = [(pdf.pages[i].extract_text(use_text_flow=True) or "")
                 for i in parse_pages(page_spec, len(pdf.pages))]
    n_pages = len(pages)
    total_chars = sum(len(p) for p in pages)

    # lines that appear on at least half the pages are treated as headers/footers
    counts = Counter()
    for p in pages:
        counts.update({_line_key(l) for l in p.splitlines() if l.strip()})
    repeated = {k for k, c in counts.items() if n_pages >= 3 and c >= n_pages / 2}

    paras, buf = [], []

    def flush():
        if buf:
            paras.append(norm_space(" ".join(buf)))
            buf.clear()

    for p in pages:
        for line in p.splitlines():
            s = line.strip()
            if not s:
                flush()
                continue
            if _line_key(s) in repeated or re.fullmatch(r"(page\s*)?\d+(\s*of\s*\d+)?", s, re.I):
                continue
            if is_heading(s):
                flush()
                paras.append(s)
                continue
            starts_new = bool(re.match(r"^([A-Z0-9•\-–(]|\d+\.)", s))
            prev_ends = bool(buf) and buf[-1].rstrip().endswith((".", ":", ";", "?", "!"))
            if buf and prev_ends and starts_new:
                flush()
            buf.append(s)
        flush()  # never merge across pages
    return paras, total_chars


# ---------- TXT ----------
def txt_paragraphs(path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [norm_space(b) for b in re.split(r"\n\s*\n", text) if b.strip()]


def main():
    meta = pd.read_csv(METADATA, dtype=str).fillna("")
    out, report = [], []

    for _, m in meta.iterrows():
        path = find_raw_file(m["doc_id"])
        if not path:
            continue
        note = ""
        if path.suffix == ".pdf":
            paras, chars = pdf_paragraphs(path, m.get("pdf_pages", ""))
            if chars < 500:
                note = "very little text: probably a scanned PDF, needs OCR"
        elif path.suffix in (".html", ".htm"):
            paras = html_paragraphs(path)
        else:
            paras = txt_paragraphs(path)

        kept = [p for p in paras if len(p) >= MIN_CHARS and not BOILERPLATE.search(p[:120])]
        # drop exact duplicates within a document
        seen, unique = set(), []
        for p in kept:
            if p not in seen:
                seen.add(p)
                unique.append(p)

        for i, text in enumerate(unique, 1):
            out.append({
                "segment_id": f"{m['doc_id']}-p{i:03d}",
                "doc_id": m["doc_id"], "company": m["company"], "doc_type": m["doc_type"],
                "date": m["date"], "event_tag": m["event_tag"],
                "seg_index": i, "n_chars": len(text), "text": text,
            })
        report.append((m["doc_id"], path.suffix, len(paras), len(unique), note))

    df = pd.DataFrame(out)
    df.to_csv(SEGMENTS, index=False)

    print(f"{'doc_id':22} {'type':6} {'raw':>5} {'kept':>5}  note")
    for doc_id, ext, n_raw, n_kept, note in report:
        print(f"{doc_id:22} {ext:6} {n_raw:5d} {n_kept:5d}  {note}")
    print(f"\n{len(df)} segments from {len(report)} documents written to {SEGMENTS}")
    print("Next: open segments.csv and skim a few documents to check that paragraphs look right.")


if __name__ == "__main__":
    main()
