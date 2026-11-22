# v0.2.0 real-report commercial gate

## Decision

`esg-commitment-audit v0.2.0` passed the frozen commercial extraction gate on
2026-11-21. Paid-service and Codex plugin development were therefore opened.

The gate measures extraction and classification quality on target-rich pages
from four official public reports. It does not establish legal compliance,
assurance, truthfulness, or environmental performance.

## Frozen result

| Metric | Result | Gate |
|---|---:|---:|
| Reviewed candidates | 73 | informational |
| True-positive candidates | 72 | informational |
| Candidate precision | **98.63%** | ≥80% |
| Manual unique commitments | 80 | 80–100 |
| Recalled unique commitments | 75 | informational |
| Unique-commitment recall | **93.75%** | ≥85% |
| E/S/G top-level accuracy | **100%** | ≥90% |
| Subcategory accuracy | 97.22% | informational |
| Page citation coverage | **100%** | 100% |
| Duplicate candidates | 0 | 0 |

Reproduce:

```powershell
python validation\check_gate.py
```

The machine-readable review is
`validation/real_report_review_v011_gate_2026-11-21.json`.

## Reports

| Report | SHA-256 | Reviewed evidence pages |
|---|---|---|
| Microsoft, *2026 Environmental Sustainability Report* | `20918e9fc4a02241f55d12f1f5b6228a832b706499f9963a1a3f91e3d3e693ba` | 8, 17, 26, 27, 37, 48, 49 |
| Apple, *Environmental Progress Report 2025* | `597676e8b48ac45529303abc7ef47425ca62ff4efc3a375962a077a033525f74` | 5, 10, 21, 90, 92 |
| 宁德时代, *2024 年 ESG 报告* | `e16ec727d5959b91586c44edcf1deedf5d3ae29133e798a0529daaea90f535f2` | 25, 26, 27, 43, 45, 46, 48, 51, 57, 63, 79, 88, 90, 92, 97, 104, 109, 111 |
| 立讯精密, *2024 可持续发展报告* | `6cbdfa0cee22471a914bda8b6fb9b452e1806f21fa316f0f0c7e9b7ca4b9d10` | 20, 21, 31, 51, 74 |

The official PDFs remain in the local ignored audit directory and are not
redistributed.

## Review rule

A unique commitment must contain at least one of:

- a future-directed target;
- a quantified goal;
- a concrete recurring obligation.

Historical results, methods, generic governance descriptions, citations,
third-party progress with no company obligation, and duplicate restatements are
excluded.

This is a single-reviewer Codex adjudication under the written rules. The author
explicitly waived an independent second human reviewer. That waiver is recorded
as a governance decision and does not convert the review into independent
validation.

## Known misses

The five recalled-manual misses in the frozen sample are:

- Apple supplier F-GHG 90% abatement target;
- Apple 100% corporate-facility waste-diversion target;
- 立讯精密 supply-chain green low-carbon target statement;
- 立讯精密 AWS five-dimension water-management targets;
- 立讯精密 clean-technology R&D investment target.

One candidate was a false positive: a generic supplier sustainability-capability
statement without a quantified or periodic obligation.

## Remaining risk

- The review sample is target-rich and requires author-governed manual labels.
- Complex infographics and merged-cell tables can still create extraction or
  evidence-boundary errors.
- Large PDFs take materially longer than plain text and need asynchronous
  processing in hosted mode.
- Rule changes after this freeze require a new candidate snapshot and a fresh
  gate calculation.
