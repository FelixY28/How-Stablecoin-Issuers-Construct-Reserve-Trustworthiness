# Corpus decisions

Every decision about what enters the corpus, with the reason. Audit trail alongside `codebook/CHANGELOG.md`.

## D1 — Tether's response to the S&P downgrade (E3), 2026-11-22
- **Problem:** no press release on tether.io. The response exists only as (a) a spokesperson statement quoted by journalists and (b) CEO Paolo Ardoino's posts on X.
- **Decision:** include both, as separate documents with different `doc_type`: `media_quote` (T-MQ-20251126) and `x_post` (T-X-20251126, T-X-20251130).
- **Reason:** they are different channels of evidence talk. Keeping them apart lets the analysis compare what the company says officially, what the CEO says personally, and what reaches readers through a journalist's selection.
- **Caveat:** the media quote is secondary; the journalist chose which sentences appear.
- **T-X-20251130 in scope:** although it replies to Arthur Hayes, the post names S&P's method directly ("S&P made the same mistake..."). Text copied by hand from X on 2026-11-22.
- **Open:** the CEO's X bio says "Views are my own". Decide whether x_post documents are excluded, kept but reported separately from official texts, or pooled.

## D2 — GENIUS Act signing-day statements (E1), 2026-11-22
- **Problem:** neither issuer published a statement on the signing day. Nearest texts: Circle's blog on House passage (2025-07-17, falls in P0) and Tether's Q2 2025 attestation press release (late July, a different genre).
- **Decision:** do not substitute. Remove T-PR-20250718 and C-PR-20250718.
- **Reason:** a substitute from another date or genre cannot represent how the issuers spoke at the moment of E1.
- **Consequence:** Circle has no issuer text in P1.
- **Treated as a finding:** the choice of channel and timing (Circle published on its own blog before the vote; Tether spoke through its CEO in the media) is reported in the memo.

## D3 — OCC final rule (E9), 2026-11-22
- **Problem:** no issuer text in the corpus falls near E9 (2026-10-21).
- **Decision:** remove E9 from `events.csv` and from sub-question 2; the study period now ends with E8 (August 2026).
- **Reason:** insufficient evidence to say anything about shifts around E9. Listed under future work.

## D4 — Legal disclaimers in issuer texts, 2026-11-22
- **Decision:** delete forward-looking-statement notices, endorsement disclaimers and numbered product footnotes from issuer texts (rule `DISCLAIMER` in `scripts/02_clean_segment.py`).
- **Reason:** readers do not read them, and they are legal boilerplate rather than the issuer constructing trust.
- **Not applied to attestation reports:** their limitation and restriction-of-use clauses are data for sub-question 3.
- **Exception kept:** the USAT "not legal tender / not issued, backed or approved by the U.S. government" notice (T-PR-20260127). It is a disclaimer, but its content explicitly denies state backing, which bears directly on AUTH_STATE.

## Cleaning fix (not a decision) — tether.io "latest news" block, 2026-11-22
- The downloaded tether.io pages include a "latest news" block dated 19 November 2026 (the download date), which is not part of the press releases. Removed at HTML parsing.

## D5 — Auditor procedure lists, 2026-11-22
- **Decision:** keep each bulleted list of procedures in the attestation reports ("we carried out the following procedures: ...") as one segment.
- **Reason:** the comparison in sub-question 3 is about the overall depth of the assurance work, which the list expresses as a whole.
