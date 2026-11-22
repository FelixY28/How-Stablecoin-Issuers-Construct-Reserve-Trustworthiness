# Codebook changelog

Record every change: what changed, why, and which segments prompted it.
This file is the audit trail that supports dependability and confirmability.

## v0.1 — initial draft
- Nine deductive codes derived from the research question (sources of authority, hedging, rebuttal, confirmation narrative).
- Examples drawn from publicly reported issuer statements, 2025–2026.

## v0.2 — 2026-11-22, after hand-coding 20 development segments
Basis: 20 of the 30 segments in `analysis/dev_coding.csv`, coded by the researcher against v0.1, then compared with an independent second reading by Claude. Disagreements showed which definitions could be read more than one way. All six changes were approved by the researcher.

- **R1 CONFIRMATION — two-part test.** Change: apply only if (a) an external requirement, standard or validation is named and (b) the issuer says it already met it / it validates the existing approach; (b) alone is SELF_ASSURANCE. Reason: CONFIRMATION was applied to 13/20 segments, mostly self-praise with no external standard. Segments: T-MQ-20251126-p003, T-PR-20250912-p005, C-PR-20260225-p027; textbook case C-YR-2025-p106 was missed.
- **R2 General rule: most paragraphs get no code.** Change: code only paragraphs that argue why the issuer should be trusted; accounting notes, asset or product descriptions, figures and headings get none; code function, not keywords. Reason: no segment was left uncoded, while about 11/20 make no trust claim (codes followed words such as "law", numbers, "becoming"). Segments: C-PR-20260225-p042, C-AR-202606-p012, C-YR-2025-p068, C-AL-2025-p013.
- **R3 HEDGE_PENDING narrowed** to unfinished compliance, approval, audit or verification; general ambitions excluded. Reason: applied to visions and outlooks. Segments: C-AL-2025-p029, C-YR-2025-p009, C-YR-2025-p106.
- **R4 AUTH_STATE vs AUTH_POLITICAL boundary.** Change: regulated / licensed / compliant / regulatory standards -> AUTH_STATE; dollar, nation, geopolitics, officials -> AUTH_POLITICAL; cross-references added to both exclude fields. Reason: "U.S.-regulated" coded as political; strongest political paragraph coded otherwise. Segments: T-PR-20250912-p005, T-PR-20250912-p013, C-YR-2025-p011, T-PR-20260127-p003.
- **R5 Attestation reports are not coded with this codebook.** Change: the codebook covers issuer texts only; attestation reports are analysed by hand in `analysis/report_comparison.md` (sub-question 3). Reason: in auditor reports the speaker is the auditor or management, not the issuer constructing trust (e.g. C-AR-202512-p005 is management's assertion). Effect: `03_llm_code.py` skips attestation segments by default.
- **R6 Code each paragraph on its own.** Change: no use of document context; REBUTTAL only when the paragraph itself disputes a criticism. Reason: segments from a rebuttal document invite context-based coding. Segment: T-MQ-20251126-p003.
- Examples added from development segments (T-MQ-20251126-p003, T-PR-20250912-p005, T-PR-20260127-p003, C-YR-2025-p106). These segments are excluded from the validation sample.
