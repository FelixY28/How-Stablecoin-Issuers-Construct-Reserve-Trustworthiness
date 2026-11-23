# Evidence Talk: How Stablecoin Issuers Construct Reserve Trustworthiness (2025–2026)

A small mixed-methods study of how Tether and Circle build claims of reserve trustworthiness in their public texts, from the signing of the US GENIUS Act (July 2025) to Tether's first full audit result (August 2026).

> Status: closed as a pilot (November 2026). Full write-up in `memo.md`.

## Research question

How did Tether and Circle construct *evidence* of reserve trustworthiness in their public texts in 2025–2026, which sources of authority did they invoke, and how did their claims shift around key events?

Sub-questions:
1. Which sources of authority does each issuer invoke: the state, professional bodies, market performance, technology, or politics?
2. Do Tether's claims shift around key events (S&P downgrade, Big Four audit announcement, audit result)? Circle's texts all fall after the S&P downgrade, so Circle is not compared across phases.
3. How does the assurance claimed in press releases compare with the assurance actually provided in attestation reports?

## Data

| Type | Scope |
|---|---|
| Issuer texts | Press releases, blog posts, annual letters, an earnings release, CEO posts on X and media-quoted statements around eight key events (see `data/events.csv`); `doc_type` records the channel |
| Attestation reports | Four reserve reports per issuer (Tether: BDO; Circle: monthly reserve reports) |

All sources are public. `data/sources.csv` lists every document with its URL; `data/metadata.csv` records retrieval time and a SHA-256 hash of each file. Raw files are not committed.

## Method

1. **Corpus construction**: download, hash and log each document (`scripts/01_collect.py`).
2. **Segmentation**: extract text from HTML/PDF, remove headers and footers, split into paragraphs (`02_clean_segment.py`).
3. **Codebook**: nine deductive codes on sources of authority and stance (`codebook/`). v0.2 tightens four codes after hand-coding 20 development segments; revisions are logged in `codebook/CHANGELOG.md`.
4. **LLM-assisted coding**: each paragraph coded by an LLM against the codebook (`03_llm_code.py`).
5. **Validation**: a blind manual sample compared with the LLM codes; per-code agreement and Cohen's kappa (`04_sample_manual.py`, `05_agreement.py`). With a single human coder this measures human–LLM agreement, not inter-coder reliability.
6. **Descriptive analysis**: share of paragraphs per code by issuer and event phase (`06_analysis.py`).
7. **Close reading**: thematic and document analysis of selected paragraphs, and a structured comparison of attestation reports (`analysis/report_comparison.md`).

The computational step points to *where* to read; the interpretation comes from close reading.

## Findings

1. **Different sources of authority.** Circle invokes almost only one source of authority, the state (charter, federal supervision); Tether spreads its claims across self-assurance, market performance, professional and state authority. Within press releases, state authority appears in 88% of Circle's segments and 26% of Tether's, while professional authority appears in none of Circle's. Genre mix and event-based selection differ between issuers, so only like-for-like comparisons are read as issuer differences.
2. **Channel division of labour.** Official texts build trust (self-assurance 47%, professional authority 28%, market performance 29%; rebuttal 3%); the CEO's X posts are dominated by rebuttal (31%) and cite no state or professional authority (n = 13).
3. **Claimed versus provided assurance.** Tether's audit press release turns KPMG's opinion that the 2025 financial statements "present fairly" the position "as of December 31, 2025" into "the proof of that stability"; an opinion on one past date is presented as evidence of ongoing resilience. The quarterly BDO attestations are narrower still (one date, normal market conditions). Between Tether's earliest and latest reports, the template is identical, but the engaging party, responsible party and signing entity all change.

The apparent shift from state to professional authority across event phases tracks which documents fall in each phase, and is reported as a sampling effect.

## Limitations

- Small corpus, limited to issuers' own texts, plus one statement known only through a journalist's selection of quotes.
- One human coder; the analysis uses LLM codes throughout, with the manual sample used for validation only.
- CONFIRMATION and HEDGE_PENDING were over-applied under v0.1 and narrowed in v0.2 before the LLM coding (see CHANGELOG); human–LLM agreement on these codes remains low, so their shares are read with caution.
- Shares are descriptive; no statistical inference is attempted.
- All event dates verified against primary sources (`data/events.csv`). Corpus decisions and their reasons are logged in `analysis/corpus_decisions.md`.
- No issuer statement exists for the GENIUS Act signing day; the gap is reported, not filled with substitutes.

## Future work

Add regulatory comment letters and the OCC rule preamble, litigation documents, on-chain data, and interviews with compliance staff and auditors.

## Reproduce

```bash
pip install -r requirements.txt
cd scripts
python 01_collect.py
python 02_clean_segment.py
python 04_sample_manual.py --dev # 30 development segments -> analysis/dev_coding.csv; revise codebook
python 03_llm_code.py            # needs ANTHROPIC_API_KEY, or see the script header for other providers
python 04_sample_manual.py       # blind validation sample (excludes dev segments); code analysis/manual_coding.csv by hand
python 05_agreement.py
python 06_analysis.py
```
