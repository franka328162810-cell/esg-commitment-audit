# v0.1.1 disputed-sample decisions

These decisions apply the annotation rule used in
`real_report_review_v011_2026-11-21.json`: a commitment must contain a future
target, quantified goal, or concrete recurring obligation. Historical results,
methods, governance descriptions, vague aspirations, and duplicates are
excluded.

| Report | Candidate | Decision | Reason |
|---|---|---|---|
| Microsoft | `c002` | True positive | Explicit carbon-negative target for 2030. |
| Microsoft | `c003` | True positive | Explicit water-positive target for 2030. |
| Microsoft | `c004` | True positive | Explicit zero-waste target for 2030. |
| Microsoft | `c018` | True positive | Contains the explicit 40% water-usage-effectiveness reduction target. |
| 宁德时代 | `c004` | True positive | Company target: core operations carbon neutral in 2025. |
| 宁德时代 | `c006` | True positive | Company target: value-chain carbon neutral in 2035. |
| 宁德时代 | `c005` | False positive | China’s 2030 carbon-peaking target, not a CATL commitment. |
| 宁德时代 | `c007` | False positive | China’s 2060 carbon-neutrality target, not a CATL commitment. |
| 宁德时代 | `c012` | True positive | Requires strategic suppliers to set pollutant and waste reduction targets. |
| 宁德时代 | `c013` | True positive | Although partly historical, the sentence contains a continuing expansion and reduction obligation. |
| Apple | `c001` | True positive, compound | Bundles water replenishment by 2030 and plastic removal by 2025. |
| Apple | `c002` | True positive | Explicit carbon-neutrality target for 2030. |
| Apple | `c003` | True positive, compound | Bundles the AWS certification target with the supplier water-reuse target. |
| Apple | `c004` | True positive, compound | Bundles recycled/renewable materials, water stewardship, and landfill-waste goals. |
| Apple | `c007` | False positive, duplicate | Repeats the Apple 2030 carbon goal already represented by `c002`. |
| Apple | `c008` | True positive, mixed | Contains the 100% clean-electricity-by-2030 target inside roadmap text. |
| Apple | `c009` | True positive | Explicit 90% emissions-reduction target by 2050. |
| Apple | `c033` | True positive, compound | Contains water replenishment, AWS certification, and supplier water-reuse targets mixed with progress. |
| 立讯精密 | `c005` | True positive, compound | Contains two board-composition targets. |
| 立讯精密 | `c006` | True positive | Explicit 100% ethics-complaint handling target. |
| 立讯精密 | `c007` | True positive | Explicit 100% employee-integrity-letter signing target. |
| 立讯精密 | `c008` | True positive | Multi-year clean-energy-use targets through 2025. |
| 立讯精密 | `c009` | True positive | Water-withdrawal efficiency target for 2025 against a 2021 baseline. |
| 立讯精密 | `c010` | True positive, compound | Merges many target and progress cells; contains Scope 3 and supplier targets. |
| 立讯精密 | `c015` | True positive, compound | Contains Scope 1/2, Scope 3, and 2050 carbon-neutrality targets. |
| 立讯精密 | `c016` | False positive | General water-saving actions without a quantified target. |
| 立讯精密 | `c017` | False positive | Site-level efficiency aspiration without a quantified target. |

Candidates marked “compound” or “mixed” count as true positives for
candidate-level precision, but they are still product defects because a
commitment should be emitted as one atomic, reviewable item.
