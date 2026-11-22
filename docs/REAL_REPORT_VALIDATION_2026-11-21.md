# Real-report validation — 2026-11-21

## Decision

`esg-commitment-audit v0.1.0` should **not** enter paid service or formal Codex
plugin development yet.

The reference implementation proves the concept, but it does not meet the
minimum precision and context-handling requirements for a paid assurance
workflow. It remains a free research prototype.

## Reports reviewed

| Report | Language | Pages | Source |
|---|---|---:|---|
| Microsoft, 2026 Environmental Sustainability Report | English | 66 | [Microsoft official report page](https://www.microsoft.com/en-us/corporate-responsibility/topics/sustainability/report/) |
| 宁德时代 2024 年 ESG 报告 | Chinese | 170 | [深圳证券交易所 public disclosure](https://disc.static.szse.cn/download/disc/disk03/finalpage/2025-03-15/c90b92f8-9d52-49d2-9c13-3c10906d0ed6.PDF) |

The PDFs are not redistributed in this repository. Their SHA-256 values and
sampling page numbers are recorded in
`validation/real_report_review_2026-11-21.json`.

## Review method

This was a single-reviewer manual adjudication performed by the Codex assistant.
It is not an independent human expert review and must not be described as one.

A candidate was counted as a unique commitment only when it contained a
future-directed target or obligation. Historical achievements, methodology
descriptions, current governance arrangements, completed actions, general
principles, and duplicate restatements were excluded.

Pages reviewed:

- Microsoft: PDF page 62, printed page 62.
- CATL: PDF pages 66, 71, 87–92; printed pages 63, 68, 84–89.

## Results

### Full-document scan

| Report | Detected candidates | Average score | Candidates at moderate/high structure |
|---|---:|---:|---:|
| Microsoft | 115 | 0.0960 | 0 |
| CATL | 188 | 0.1011 | 0 |

The full scan produced 303 candidates. All were classified below 0.50, showing
that the sentence-level scorer does not assemble evidence distributed across a
report.

### Manually reviewed sample

| Metric | Result |
|---|---:|
| Sampled candidates | 37 |
| True-positive candidates | 13 |
| False-positive candidates | 24 |
| Unique manual commitments in the sampled pages | 14 |
| Manually identified commitments recalled | 14 |
| Candidate precision | 35.1% |
| Manual commitment recall | 100% |
| E/S/G category accuracy among true-positive candidates | 76.9% |
| Subcategory accuracy among true-positive candidates | 53.8% |
| Correct page citation among sampled candidates | 100% |

The high recall applies only to the small, explicitly target-bearing sample.
It does not establish recall across the full reports.

## Representative failures

### False positives

- Microsoft: achieved renewable-energy, waste-diversion, recycling, and
  ecosystem-project metrics were treated as commitments.
- CATL: current governance arrangements, completed procedure revisions,
  scenario-selection methodology, regulatory compliance descriptions, and
  duplicate tables were treated as commitments.

### Classification failures

- Microsoft’s water-positive commitment was assigned to biodiversity.
- CATL’s COD target was assigned to governance.
- CATL’s hazardous-waste target was assigned to supply chain.
- CATL’s RTO/VOCs commitment was assigned to governance.

### Context and segmentation failures

- One Microsoft candidate bundled four bullet-point achievements into one
  “commitment.”
- One CATL candidate bundled two carbon-neutrality target years into one item.
- Repeated target tables were not deduplicated.
- Owners and assurance evidence located elsewhere in the report were ignored
  because v0.1.0 scores individual sentences without surrounding context.

## Release gate

The paid service and formal plugin should remain blocked until a later version
meets all of the following on a larger, independently reviewed set:

1. candidate precision at least 80%;
2. unique-commitment recall at least 85%;
3. E/S/G category accuracy at least 90%;
4. every finding linked to a source page and paragraph/table row;
5. duplicate commitments merged across repeated sections;
6. owner, baseline, target, assurance, and review evidence assembled from
   surrounding sections rather than one sentence;
7. a second human reviewer adjudicates the disagreement set.

The next technical step should be extraction stabilization, not billing or
plugin packaging.
