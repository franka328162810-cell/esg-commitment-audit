# Methodology

## Purpose

The workbench evaluates the written structure of an ESG or climate commitment.
It asks three questions:

1. **Observability (`V_obs`)** — can a reader identify the target, baseline,
   boundary, timeframe, evidence, and verification method?
2. **Enforceability (`V_enf`)** — is responsibility assigned, is progress
   reportable, is the undertaking binding, and is there a remedy for failure?
3. **Reversibility (`V_rev`)** — are review, revision, withdrawal, rollback, or
   mitigation paths specified?

The overall score is:

```text
CRV = 0.35 * V_obs + 0.35 * V_enf + 0.30 * V_rev
```

This follows the public ICS anchor document v2.2, section 7.3. Alternative
presets are provided for different review purposes, but the report always
records the selected weights.

## Evidence rule

A check can receive points only when the analyzer detects source text or a
source-derived field that supports it. For example:

- a numeric target and unit support target measurement;
- an explicit baseline year supports baseline traceability;
- a board or committee reference supports ownership;
- an annual review clause supports revisability.

Missing evidence is shown as missing. The analyzer does not fill gaps with
plausible assumptions.

## Dimension checks

### Observability — total 1.00

| Check | Weight |
|---|---:|
| Quantified target | 0.30 |
| Baseline year/value | 0.20 |
| Boundary, scope, or responsible owner | 0.15 |
| Target year or interim milestones | 0.15 |
| Measurement standard or method | 0.10 |
| Assurance or periodic progress disclosure | 0.10 |

### Enforceability — total 1.00

| Check | Weight |
|---|---:|
| Named owner or oversight body | 0.15 |
| Progress reporting or milestones | 0.15 |
| Regulatory, contractual, or remuneration-linked binding | 0.25 |
| Remedy, penalty, corrective action, or escalation | 0.20 |
| External assurance | 0.10 |
| Dependencies are controlled or a fallback is disclosed | 0.15 |

### Reversibility — total 1.00

| Check | Weight |
|---|---:|
| Review or revision mechanism | 0.25 |
| Revision trigger or review cadence | 0.20 |
| Withdrawal or exit reporting procedure | 0.20 |
| Mitigation, compensation, or rollback path | 0.20 |
| Interim milestones or staged implementation | 0.15 |

## Interpretation bands

| Score | Label | Meaning |
|---:|---|---|
| 0.00–0.30 | Low structure | Core evidence is mostly absent. |
| 0.30–0.50 | Limited structure | Some elements exist, but major gaps remain. |
| 0.50–0.70 | Moderate structure | Reviewable with substantial clarification. |
| 0.70–0.85 | High structure | Most requested elements are explicit. |
| 0.85–1.00 | Very high structure | The text is unusually complete on the implemented checks. |

These labels describe the written commitment only.

## AI Policy Revision Audit Beta

The Beta applies a separate, non-scoring structural checklist to AI policies,
model cards, governance procedures, and similar written controls:

| Check | What the analyzer looks for |
|---|---|
| Scope and owner | Applicability, effective date, policy owner, or accountable body |
| Review cadence | A recurring review or reconsideration commitment |
| Revision process | Who may propose or approve amendments, and through what process |
| Version history | A change log, revision history, and retained prior versions |
| Advance notice | Notice period and communication to affected people |
| Appeal and human review | A route to challenge a decision or obtain human review |
| Refusal and exit | Opt-out, refusal, withdrawal, or exit procedure |
| Monitoring and audit | Logs, records, monitoring, and evidence review |
| Rollback and deprecation | Suspension, rollback, or retirement conditions |
| Independent oversight | Review by an external auditor, panel, or ethics body |

Each check is reported as `present`, `partial`, or `missing` together with the
matching source excerpt. Presence means only that the examined text contains a
recognisable written control. It does not establish implementation quality,
legal compliance, or actual system behaviour.

The Beta is informed by the revision-oriented framing in Xue, Z. (2026), *On
Recursive Freedom: A Theory of the Freedom to Revise*, DOI
[10.5281/zenodo.24217876](https://doi.org/10.5281/zenodo.24217876). The
implementation is an engineering interpretation for document review. The
publication is not evidence that the rule engine has been independently
validated.

The Beta must not be used to score an individual's personality, mental state,
political views, employability, creditworthiness, insurance risk, educational
outcomes, immigration status, or legal culpability.
