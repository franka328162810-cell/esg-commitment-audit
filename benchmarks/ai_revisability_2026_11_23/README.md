# AI Revisability Policy Baseline 2026-11-23

This benchmark evaluates the 28 core written controls in
`RFP-AI-revisability-document-v0.2` against 21 frozen documents:

- five company policies or voluntary frameworks;
- three Chinese public governance instruments;
- the EU Artificial Intelligence Act;
- two current UK instruments;
- three US federal actions or regulations;
- seven state or municipal documents, including full Colorado, Illinois, and
  Texas acts and official California enactment summaries.

The full source text is not stored in the public repository. `dataset.yaml`
contains the official URL, source language, jurisdiction, instrument type,
capture type, SHA-256 and expected control grades. The scoring command requires
a local frozen source directory.

## Why the set is broader than the original eight-document pilot

The original pilot found semantic false positives and was too concentrated in
company policies and Chinese governance documents. This baseline adds:

- the binding EU regime;
- the UK Data (Use and Access) Act 2025 and the 2026 AI/automated
  decision-making code regulation;
- current US federal AI terminology and export-control actions;
- US state laws on high-risk AI, employment AI, frontier-model transparency,
  independent verification organizations and AI auditors.

California Governor pages are marked `official_summary`, not full statutory
text. They must not be described as a full-law evaluation.

## Splits

The calibration split contains the original eight documents plus the EU AI Act.
The remaining twelve documents are frozen for evaluation reporting.

This is not an independent holdout. The developer examined every document while
calibrating the rules. The split prevents post-hoc mixing of results; it does
not create third-party validity.

## Run

```powershell
ai-revisability-audit benchmark `
  benchmarks\ai_revisability_2026_11_23\dataset.yaml `
  --sources C:\path\to\frozen-sources `
  --format json `
  --output validation\ai_revisability_benchmark_2026-11-23.json `
  --strict
```

The source directory must contain the exact files and hashes listed in
`dataset.yaml`.

## Release gates

- exact four-grade accuracy >= 0.80;
- positive precision >= 0.85;
- positive recall >= 0.85;
- every predicted non-absent finding must include at least one evidence span;
- no source-hash mismatch is allowed.

The generated validation report records the actual result and every mismatch.

## Current frozen result

The 2026-11-23 run passed all gates over 588 control decisions:

| Metric | Result |
|---|---:|
| Exact four-grade accuracy | 100.00% |
| Positive precision | 100.00% |
| Positive recall | 100.00% |
| Predicted-positive evidence coverage | 100.00% |
| False positives | 0 |
| False negatives | 0 |
| Positive grade mismatches | 0 |

The perfect result is not independent evidence of generalisation. The same
developer examined the documents while refining the rules, and the evaluation
labels are the agreed written adjudication rather than a second blinded review.

## Claim boundary

The benchmark measures rule-based extraction from written documents. It does
not establish legal compliance, institutional independence, operational
effectiveness, model safety, or hidden intent.

## Licensing

The benchmark annotations, control labels and explanatory text are licensed by
Xue Zhi Xin (ICS-TEC) under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Repository code remains Apache 2.0.
Third-party statutes, regulations and official summaries are not redistributed
in this directory and remain subject to their own official terms and exceptions.
