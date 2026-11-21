# Rule provenance

The public v0.2.0 implementation derives its high-level method from:

- ICS Anchor Document v2.2, section 3.3 (`REV`) and section 7.3 (`CRV`);
- the author's CRV-ESG implementation specification, which defines
  observability, enforceability, and reversibility sub-dimensions;
- the project delivery rules requiring Apache 2.0 reference implementation,
  permanent free academic use, and a CC BY-SA 4.0 path for formalizations.

The v0.2.0 implementation intentionally simplifies the larger CRV-ESG design:

- deterministic bilingual rules instead of an LLM extraction dependency;
- weighted arithmetic aggregation only;
- no Monte Carlo simulation or inter-rater reliability claim;
- no claim of external calibration.

These divergences are recorded so that later versions can be compared against
the original specification without presenting v0.2.0 as the full CRV-ESG
implementation.
