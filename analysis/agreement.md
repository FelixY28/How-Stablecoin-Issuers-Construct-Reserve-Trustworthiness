# Human-LLM agreement

Segments compared: 30. One human coder versus the LLM; this is not inter-coder reliability.

Kappa guide (Landis & Koch): >0.8 almost perfect, >0.6 substantial, >0.4 moderate.
Kappa is unstable when a code is rare in the sample; read it together with the counts.

| code | n | human_yes | llm_yes | agreement | kappa | interpretation |
|---|---|---|---|---|---|---|
| AUTH_STATE | 30 | 1 | 6 | 0.833 | 0.242 | fair |
| AUTH_PROF | 30 | 4 | 3 | 0.967 | 0.839 | almost perfect |
| AUTH_MARKET | 30 | 0 | 5 | 0.833 | 0.0 | poor |
| AUTH_TECH | 30 | 2 | 0 | 0.933 | 0.0 | poor |
| AUTH_POLITICAL | 30 | 0 | 4 | 0.867 | 0.0 | poor |
| SELF_ASSURANCE | 30 | 4 | 8 | 0.8 | 0.392 | fair |
| HEDGE_PENDING | 30 | 3 | 2 | 0.9 | 0.348 | fair |
| REBUTTAL | 30 | 2 | 3 | 0.967 | 0.783 | substantial |
| CONFIRMATION | 30 | 0 | 2 | 0.933 | 0.0 | poor |

## Next steps
1. Read analysis/disagreements.csv code by code.
2. For each disagreement decide: was the LLM wrong, were you wrong, or is the definition unclear?
3. Unclear definitions -> revise the codebook, log it in codebook/CHANGELOG.md, save as a new version, rerun 03.