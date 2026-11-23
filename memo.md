# Evidence Talk: How Stablecoin Issuers Construct Reserve Trustworthiness

*Research memo, mini-project close-out, November 2026. Hongzheng You.*

## 1. Why evidence matters for stablecoin trust

A fiat-backed stablecoin is a promise that each token can be redeemed for one dollar. Almost no holder can check the reserves behind that promise. Trust therefore depends on evidence produced by others: auditors' reports, regulators' licences, market track records, and the issuer's own statements about all of these. This memo asks how Tether and Circle constructed that evidence in their public texts between the signing of the GENIUS Act (July 2025) and Tether's first full audit result (August 2026). It also asks how far the assurance they claim matches the assurance their attestation reports actually provide.

## 2. Data and method

- **Corpus.** Issuer press releases, an earnings release, an annual letter, a year-in-review blog post, media quotes and CEO posts on X, plus four reserve attestation reports per issuer (Tether/BDO, quarterly; Circle, monthly). All public; each file is hashed and logged in `data/metadata.csv`. Documents are split into paragraph segments.
- **Codebook.** Nine deductive codes on sources of authority (state, professional, market, technical, political), self-assurance, pending claims, rebuttal and confirmation narratives (`codebook/`).
- **Coding.** Every segment was coded by an LLM against the codebook. One human coder blind-coded a stratified sample for validation only; LLM codes are used throughout the analysis so that a single, consistent coder underlies all shares. Human–LLM agreement per code is reported in `analysis/agreement.md` (this is not inter-coder reliability). A further 20 development segments were hand-coded to revise the codebook to v0.2.
- **Close reading.** The computational shares point to where to read. Interpretation comes from close reading of selected segments and from a structured, clause-by-clause comparison of attestation reports (`analysis/report_comparison.md`).

## 3. Findings

### Finding 1: The two issuers lean on different sources of authority

**Claim.** Circle invokes almost only one source of authority, the state; Tether spreads its claims across several (self-assurance, market performance, professional and state authority).

**Evidence.** Code shares by issuer (`analysis/summary_tables.md`, Tables 1–2). The contrast is sharpest within the same genre: among press-release segments, state authority appears in 88% of Circle's and 26% of Tether's, while professional authority appears in none of Circle's and 29% of Tether's. Examples: C-PR-20251212-p004 (Circle) and T-PR-20250912-p001 (Tether).

**Interpretation.** Circle can point to a US charter and federal supervision; Tether, without a comparable US status for USDT during most of the period, substitutes its own assertions and statements of what it is "progressing towards". Tether's texts also appear more often in defensive settings. **Caveat:** Tether's documents were selected around trust events, and the two issuers' genre mixes differ (Circle's corpus is dominated by blog, earnings and annual-letter text, in which far fewer segments carry any code). Only like-for-like genre comparisons should be read as issuer differences; Circle has only 17 press-release segments.

### Finding 2: Official channels build trust; the CEO's personal channel fights

**Claim.** Official texts build trust through self-assurance (47% of segments), professional authority (28%) and market performance (29%), whereas the CEO's posts on X borrow almost no authority and are dominated by rebuttal (31%).

**Evidence.** Rebuttal accounts for only 3% of official-text segments; state and professional authority are both 0% in X posts. Example rebuttal post: T-X-20251130-p006 ("S&P made the same mistake of not considering the additional Group Equity…").

**Interpretation.** The "views are my own" disclaimer enables a division of labour. The company keeps a compliant, restrained official voice, while the CEO, speaking personally, confronts critics directly without those statements counting as company positions. In Preda's terms, the personal channel does the boundary work of distinction ("we are not traditional finance"), while the official channel accumulates legitimacy. **Caveat:** only 13 X segments; the shares indicate a tendency.

### Finding 3: Claimed assurance exceeds provided assurance, and the chain behind the evidence moves

**(a) Claimed versus provided.** An opinion on one past date is presented as proof of ongoing stability. Tether's own release reports what KPMG found: the 2025 financial statements "present fairly, in all material respects, the financial position of the Company as of December 31, 2025" (T-PR-20260813-p003). The CEO's quote in the same release turns this into a forward-looking guarantee: holders "trust our Company to remain resilient amidst all the global uncertainty … the proof of that stability is no longer just a Tether promise; it's a signed opinion" (T-PR-20260813-p011). A financial-statement opinion says the accounts were fairly presented at year-end; it says nothing about resilience in the next crisis. The audit language lends professional authority to a claim the auditor never made. The quarterly BDO attestations that preceded the audit are narrower still: they cover "a point in time" (p.3) and a valuation that "does not reflect unexpected and extraordinary market conditions, or the case of key custodians or counterparties experiencing substantial illiquidity" (p.4). *Note:* the KPMG report itself is not in the corpus; its scope is taken from Tether's own description.

**(b) Earliest versus latest report.** What the reports assure did not change, but who stands behind them did. T-AR-2026Q2 adds "engaged by Tether Global Investments Fund SICAF SA" (p.2), where T-AR-2025Q1 names no engaging party; responsibility moves from "Management" (2025Q1, p.2) to "The Board of Director [sic]" (2026Q2, p.2); the signatory changes from "BDO Italia S.p.A." to "BDO Advisory Services S.r.l." (p.4). The standard (ISAE 3000 Revised), template and exclusion clauses are word for word identical. Readers who skim for the unchanged "not modified" opinion will read continuity, yet the institutional chain behind the evidence was reorganised. Why, and whether the new signatory has equivalent audit standing, are unstated and need verification.

**Comparison with Circle.** Both issuers' reports are reasonable-assurance engagements on a single report, not audits (Tether: ISAE 3000; Circle: AICPA examination). Both measure against criteria the issuer defines itself; neither cites the AICPA 2025 Criteria for Stablecoin Reporting. Circle's reports attest two dates per month (e.g., 19 and 31 March 2025), which makes month-end window dressing harder; Tether's attest one.

### What did not hold up: shifts around key events

The phase charts show a move from state to professional authority over time. On inspection this tracks which documents fall in each phase (the topics of the event-driven releases) rather than a change in how either issuer argues. It is reported as a sampling effect, not a finding.

## 4. Limitations

- Issuer texts only; small and event-selected corpus; unequal genre mix between issuers.
- One human coder; human–LLM agreement validates the LLM coder only against that coder's reading.
- The 20 development segments revealed that CONFIRMATION was applied far more widely than its definition allows (13 of 20); v0.2 narrowed it before the LLM coding. Human–LLM agreement on CONFIRMATION and HEDGE_PENDING stays low (`analysis/agreement.md`), so their shares are read with caution.
- Descriptive shares only; no statistical inference.
- No issuer statement exists for the GENIUS Act signing day; the gap is reported, not filled with substitutes.

## 5. Next steps

1. Rebuild the corpus on a keyword-based sampling frame applied equally to both issuers (reserve, attestation, audit, GENIUS, OCC, licence, compliance), to remove the genre and selection imbalance.
2. Add the KPMG audit report, the OCC rule preamble and comment letters, and litigation documents, so that issuer claims can be read against regulators' and courts' accounts of the same evidence.
3. Interviews with compliance staff, auditors and regulators on how attestation templates are negotiated, how the scope of an engagement is set, and what "a signed opinion" is taken to mean by those who rely on it.

These map onto the Trustworthy Stablecoins project's interest in how trust and evidence are coordinated between centralised issuers, professional intermediaries and regulators.
