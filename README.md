# Evidence Talk: How Stablecoin Issuers Construct Reserve Trustworthiness (2025–2026)

A small mixed-methods study of how Tether and Circle build claims of reserve trustworthiness in their public texts, from the signing of the US GENIUS Act (July 2025) to the OCC's final implementing rule (November 2026).

> Status: work in progress. Findings below are placeholders until the coding is complete.

## Research question

How did Tether and Circle construct *evidence* of reserve trustworthiness in their public texts in 2025–2026, which sources of authority did they invoke, and how did their claims shift around key events?

Sub-questions:
1. Which sources of authority does each issuer invoke: the state, professional bodies, market performance, technology, or politics?
2. Do the claims shift around key events (S&P downgrade, Big Four audit announcement, audit result, OCC rule)?
3. How does the assurance claimed in press releases compare with the assurance actually provided in attestation reports?

## Data

| Type | Scope |
|---|---|
| Issuer texts | Press releases, blog posts and annual letters around nine key events (see `data/events.csv`) |
| Attestation reports | Four reserve reports per issuer (Tether: BDO; Circle: monthly reserve reports) |

All sources are public. `data/sources.csv` lists every document with its URL; `data/metadata.csv` records retrieval time and a SHA-256 hash of each file. Raw files are not committed.

## Method

1. **Corpus construction**: download, hash and log each document (`scripts/01_collect.py`).
2. **Segmentation**: extract text from HTML/PDF, remove headers and footers, split into paragraphs (`02_clean_segment.py`).
3. **Codebook**: nine deductive codes on sources of authority and stance (`codebook/`). Revisions are logged in `codebook/CHANGELOG.md`.
4. **LLM-assisted coding**: each paragraph coded by an LLM against the codebook (`03_llm_code.py`).
5. **Validation**: a blind manual sample compared with the LLM codes; per-code agreement and Cohen's kappa (`04_sample_manual.py`, `05_agreement.py`). With a single human coder this measures human–LLM agreement, not inter-coder reliability.
6. **Descriptive analysis**: share of paragraphs per code by issuer and event phase (`06_analysis.py`).
7. **Close reading**: thematic and document analysis of selected paragraphs, and a structured comparison of attestation reports (`analysis/report_comparison.md`).

The computational step points to *where* to read; the interpretation comes from close reading.

## Findings

_To be written after analysis. See `memo.md`._

## Limitations

- Small corpus, limited to issuers' own texts.
- One human coder.
- Shares are descriptive; no statistical inference is attempted.
- Some event dates are approximate (flagged in `data/events.csv`).

## Future work

Add regulatory comment letters and the OCC rule preamble, litigation documents, on-chain data, and interviews with compliance staff and auditors.

## Reproduce

```bash
pip install -r requirements.txt
cd scripts
python 01_collect.py
python 02_clean_segment.py
python 03_llm_code.py            # needs ANTHROPIC_API_KEY, or see the script header for other providers
python 04_sample_manual.py       # then code analysis/manual_coding.csv by hand
python 05_agreement.py
python 06_analysis.py
```
