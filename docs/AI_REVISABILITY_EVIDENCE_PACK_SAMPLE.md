# AI Revisability Evidence-Pack Assessment

- Organization: **Example AI Company**
- Review date: 2026-11-23
- Profile: `general`
- Base document: `policy.md`
- Base SHA-256: `f4f7c0f16d375d348038492b3235480fd0f4ab9fe3552407c2bbc8f00c7444f8`

## Artifact inventory

| Artifact | Type | Issuer | Issued | Hash | E3 Eligible | Warnings |
|---|---|---|---|---|---|---|
| `approval-record.txt` | `approval_record` | AI Governance Board | 2026-11-20 | matched | true | — |
| `rollback-drill.txt` | `rollback_drill` | Incident Response Team | 2026-11-18 | matched | true | — |
| `monitoring-snapshot.json` | `monitoring_snapshot` | AI Operations | 2026-11-19 | matched | true | — |
| `independent-review.txt` | `independent_review` | External AI Review Panel | 2026-11-21 | matched | true | — |

## Proposed evidence-grade promotions

| Control | Baseline | Proposed | Supporting artifacts | Human confirmation |
|---|---|---|---|---|
| `accountable_owner` | `documented` | `operationally_evidenced` | `approval-record.txt` | true |
| `revision_authority` | `documented` | `operationally_evidenced` | `approval-record.txt` | true |
| `rollback_condition` | `documented` | `operationally_evidenced` | `rollback-drill.txt` | true |
| `rollback_authority` | `documented` | `operationally_evidenced` | `rollback-drill.txt` | true |
| `rollback_evidence` | `absent` | `documented` | `rollback-drill.txt` | true |
| `monitoring_metrics` | `documented` | `operationally_evidenced` | `monitoring-snapshot.json` | true |
| `audit_logs` | `documented` | `operationally_evidenced` | `monitoring-snapshot.json` | true |
| `independent_oversight` | `absent` | `independently_verified` | `independent-review.txt` | true |

## Remaining evidence gaps

- `stakeholder_participation` (absent): needs board_minutes
- `version_identifier` (documented): needs change_log, model_signature
- `change_log` (documented): needs change_log
- `prior_version_access` (documented): needs change_log
- `protected_clauses` (absent): needs approval_record, exception_log, independent_review
- `explanation` (absent): needs appeal_record
- `appeal` (absent): needs appeal_record
- `refusal_exit` (absent): needs appeal_record
- `retention` (absent): needs monitoring_snapshot
- `anti_abuse` (absent): needs exception_log, independent_review
- `uncertainty` (absent): needs evaluation_report
- `capability_gate` (absent): needs approval_record, rollback_drill, evaluation_report
- `interruptibility` (absent): needs monitoring_snapshot, rollback_drill

## Warnings

- approval-record.txt: artifact type 'approval_record' is not compatible with 'version_identifier'.

## Claim boundary

This evidence-pack review verifies declared file hashes and proposes evidence-grade changes. It does not prove that the underlying event occurred, that the issuer is authoritative, or that an independent review was adequate. Every E3 or E4 proposal requires human confirmation.
