# v0.1.1 real-report extraction validation

## Decision

`ics-commitment-audit v0.1.1-dev` still does **not** pass the commercial gate.
Paid service and formal Codex plugin development remain paused.

The extraction changes reduced obvious historical-result false positives and
added PDF table-row evidence, but the additional reports still show low
candidate precision and missed table-based targets.

## Reports

### Development set

- Microsoft, *2026 Environmental Sustainability Report*, English.
- 宁德时代, *2024 年 ESG 报告*, Chinese.

### Post-development validation set

- [Apple, Environmental Progress Report 2025](https://www.apple.com/environment/pdf/Apple_Environmental_Progress_Report_2025.pdf), English.
- [立讯精密, 2024 可持续发展报告](https://www.luxshare-ict.com/Public/Uploads/uploadfile/files/20250426/lixunjingmi2024kechixufazhanbaogao.pdf), Chinese.

The official PDFs remain in the local ignored audit directory and are not
redistributed in this repository. The candidate labels, page ranges, and PDF
hashes are recorded in
`validation/real_report_review_v011_2026-11-21.json`.

Apple and 立讯精密 began as held-out reports, but the extraction rules were
subsequently changed after their errors were inspected. They are therefore no
longer an untouched holdout, and the reported metrics may be optimistic.

## Review method

This is a single-reviewer manual adjudication by the Codex assistant. It is not
an independent human expert review. The author explicitly waived the independent
human-review requirement on 2026-11-21; this is a governance decision and does
not convert the review into independent validation.

A candidate was accepted only when it contained a future target, quantified
goal, or concrete recurring obligation. Historical results, project descriptions,
methods, governance structures, vague aspirations, and duplicates were excluded.

## Results

| Split | Sampled candidates | True-positive candidates | Candidate precision |
|---|---:|---:|---:|
| Development | 14 | 12 | 85.7% |
| Post-development validation | 17 | 14 | 82.4% |
| Total | 31 | 26 | **83.9%** |

| Split | Manual unique commitments | Recalled | Recall |
|---|---:|---:|---:|
| Development | 13 | 12 | 92.3% |
| Post-development validation | 30 | 19 | 63.3% |
| Total | 43 | 31 | **72.1%** |

| Metric | Result | Gate | Pass |
|---|---:|---:|---|
| Candidate precision | 83.9% | ≥80% | Yes |
| Unique commitment recall | 72.1% | ≥85% | No |
| E/S/G category accuracy | 88.5% | ≥90% | No, narrowly |
| Subcategory accuracy | 80.8% | Informational | — |
| Page citation coverage | 100% | 100% | Yes |
| Independent second human reviewer | Waived by author | Previously required | Waived |

The total sample contains 43 manually identified commitments, below the target
of 80–100. The review stopped at 31 candidates because recall and category
accuracy had already failed the gate and expanding the sample would not cure the
observed structural errors.

## Post-development validation failures

### Apple

- A single candidate bundled water replenishment and plastic removal commitments.
- A single candidate bundled material-recovery, water-stewardship, and
  landfill-waste goals.
- The 100% recycled cobalt, tin, gold, and rare-earth target was missed.
- The 100% corporate-facility waste-diversion target was missed.
- Repeated water targets were emitted more than once under different wording.
- Progress statements and program descriptions remained mixed with commitments.

### 立讯精密

- The target table contains many commitments whose columns are merged during PDF
  extraction.
- Targets for information-security incidents, waste conversion, wastewater
  monitoring, cumulative supplier energy savings, injury reduction, employee
  training, and 3TG responsible sourcing were missed.
- One candidate merged dozens of target and progress cells into a single item.
- Scope 1/2, Scope 3, energy, and supplier targets were not reliably separated.

### Excluded PDF

The official 美的集团 2024 ESG PDF was excluded because its text layer retained
only bullets and isolated numbers. It is a parser-compatibility failure, not a
model false positive or false negative result.

## Consequence

The engine is improving on the reports used during development but does not
generalize sufficiently. In particular, it cannot yet reconstruct merged PDF
tables or reliably reduce compound goals into atomic commitments.

The next internal milestone must remain free and non-commercial. A legal or
commercial launch before these errors are resolved would expose customers to a
high rate of manual correction and would overstate the system's assurance
quality.
