# AI Alignment Revisability Audit

Development preview: `0.4.0.dev2`

The installable Python distribution is `esg-commitment-audit`. The user-facing
command for this product is `ai-revisability-audit`.

This mode reviews whether an AI policy, constitution, model/system card, or
governance document supplies a traceable architecture for identifying,
changing, challenging, and reversing alignment rules.

The report is not a model safety test, legal compliance finding, certification,
or proof of hidden intent. Document-only review can establish text evidence; it
cannot establish that a control operated or that a model followed it.

## Local use

```powershell
ai-revisability-audit audit examples\revisability_strong_policy.md
ai-revisability-audit audit examples\revisability_strong_policy.md --format html --output audit-output\revisability.html
ai-revisability-audit compare examples\revisability_policy_v1.md examples\revisability_policy_v2.md
ai-revisability-audit serve
```

Open the local workbench at:

```text
http://127.0.0.1:8765/revisability
http://127.0.0.1:8765/revisability/versions
```

The local page does not upload documents to a hosted service.

## Hosted Beta

The hosted workbench includes `ai-revisability` as a document mode and supports
the five review profiles above:

```text
https://esg-commitment-audit-api.franka328162810.workers.dev/ai-revisability-audit
https://esg-commitment-audit-api.franka328162810.workers.dev/ai-revisability-audit/sample
https://esg-commitment-audit-api.franka328162810.workers.dev/workspace
```

The hosted mode uses the same API key, monthly document allowance, 100-page
limit, 50 MB limit, asynchronous queue, tenant isolation, and seven-day report
retention as the existing workbench. Hosted version-to-version comparison is
not yet available.

## Version trace

The version-trace mode compares a previous and current document and reports:

- checks whose evidence grade improved or regressed;
- high-materiality regressions;
- newly introduced or resolved risk warnings;
- exact statement additions and removals;
- near-identical statements paired as modifications, with a similarity value.

The comparison uses written evidence only. It cannot determine why a change was
made, who approved it, or whether the revised control operated.

## Review profiles

| Profile | Additional checks |
|---|---|
| `general` | Core alignment and governance controls |
| `news_media` | AI content provenance and editorial correction/retraction |
| `advertising` | Client disclosure and rights/consent evidence |
| `insurance` | Adverse-action explanation and human-review route |
| `industrial_design` | Design artifact provenance and design-freeze/rollback control |

Engineering-design review is intentionally deferred from the first release.

## Evidence grades

| Grade | Meaning |
|---|---|
| `absent` | The examined text did not support the control |
| `asserted` | A general claim or aspiration without a specific procedure |
| `documented` | A specific written control with supporting text |
| `operationally_evidenced` | A separate operating record demonstrates the control |
| `independently_verified` | An independent reviewer verified the evidence |
| `contradicted` | The text closes or conflicts with the control |
| `not_assessable` | The available material cannot support a conclusion |

The current document-only engine can generate `absent`, `asserted`,
`documented`, and `contradicted`. It does not automatically award
`operationally_evidenced` or `independently_verified`; those require additional
artifacts and human review.

## Core review dimensions

1. Alignment target and normative hierarchy
2. Revision authority and participation
3. Review cadence, revision triggers, and gradual change
4. Version identifier, change history, and prior-version access
5. Rollback conditions, authority, exercises, and protected clauses
6. Advance notice, explanation, appeal, refusal, and exit
7. Monitoring metrics, audit logs, and record retention
8. Independent oversight, anti-abuse controls, and uncertainty handling
9. Written capability-gate and interruption controls

## Report outputs

- JSON for machine processing
- Markdown for review and archival
- Standalone HTML for human reading
- Source spans, evidence requests, priority recommendations, warnings, and an
  explicit claim boundary

## Current limitation

This is a rule-based development preview. The hosted TXT/Markdown/DOCX/PDF path
is operational, but the product has not completed a held-out benchmark,
external methodological review, or organization-level operational-evidence
test. The next milestone is evidence-pack intake and a persistent source-change
registry.
