# Validation: adjudication and limitations

## What was compared
30 blind-coded issuer segments (of 50 drawn; the researcher stopped at 30 for time) against DeepSeek (`deepseek-chat`) codes under codebook v0.2. Agreement and Cohen's kappa in `agreement.md` are computed on the researcher's **original** codes (`manual_coding_raw.csv`), before adjudication.

## Adjudication (2026-11-22)
Each of the 29 segment-code disagreements was sorted into three groups; the researcher approved the grouping. The adjudicated codes in `manual_coding.csv` replace the LLM codes for these 30 segments in the analysis.
- **A. Researcher missed a code whose wording matches the v0.2 definition** (codes added): T-PR-20260324-p009 CONFIRMATION (verbatim codebook example); T-PR-20250912-p007 and T-PR-20260127-p012 AUTH_POLITICAL ("U.S. dollar dominance"); T-PR-20260324-p002 AUTH_MARKET (market cap, user base); C-YR-2025-p014, C-PR-20260710-p008, T-PR-20250912-p002 AUTH_STATE (MiCA, OCC/BitLicense, "U.S.-regulated"); T-X-20251126-p003 REBUTTAL; T-PR-20250912-p009 AUTH_MARKET and AUTH_POLITICAL.
- **B. Code does not fit the definition** (researcher codes removed: T-PR-20250912-p006 AUTH_TECH, C-YR-2025-p008 AUTH_TECH, C-PR-20260225-p031 SELF_ASSURANCE; LLM code rejected, researcher code kept: T-PR-20260813-p005 AUTH_MARKET).
- **C. Definition unclear** (researcher codes kept, codebook not revised; see limitations): C-YR-2025-p019 (adoption by a major financial institution: AUTH_MARKET, or a missing "institutional endorsement" code?); T-PR-20260813-p008 (an audit described as a "step forward" after years of attestations: CONFIRMATION or change?); C-AL-2025-p027 (general statement that trust is earned through reliability: SELF_ASSURANCE or no claim?).
- Remaining disagreements not assigned to a group (SELF_ASSURANCE on T-PR-20260127-p012, T-PR-20250912-p009, T-PR-20250912-p007, T-PR-20250912-p002; HEDGE_PENDING on T-PR-20250912-p002; AUTH_MARKET on T-PR-20250912-p006) keep the researcher's original code.

## Limitations to report
1. **One human coder, human-LLM agreement only**, on 30 segments; kappa is unstable for rare codes and undefined where the human applied a code to no segment (AUTH_MARKET, AUTH_POLITICAL, CONFIRMATION).
2. **The human reference was shaped by feedback.** After the development round the researcher received feedback stressing that most paragraphs carry no code. The blind codes then swung from over-coding (CONFIRMATION 13/20 in development) to under-coding (AUTH_MARKET, AUTH_POLITICAL, CONFIRMATION 0/30). Most disagreements are human omissions, so the original kappa understates how well the LLM follows the codebook.
3. **Three definitional grey zones remain** (group C above): institutional adoption, "step forward" audit framing, and general statements about trust.
4. **LLM**: a single model (DeepSeek), one run, temperature 0; no second model was compared.

## Which codes the analysis uses (decided 2026-11-22)
The descriptive analysis (`06_analysis.py`, default) uses the **LLM codes for every segment**, so all 271 issuer segments are coded by one consistent coder under codebook v0.2. The researcher's blind codes (original and adjudicated) serve only to validate the LLM. `06_analysis.py --use-human` reproduces the alternative in which adjudicated human codes replace the LLM codes for the 30 validation segments; the main patterns are the same under both.
