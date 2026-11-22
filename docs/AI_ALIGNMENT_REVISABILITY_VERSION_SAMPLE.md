# AI Alignment Revisability Version Trace

- Previous: `revisability_policy_v1.md`
- Current: `revisability_policy_v2.md`
- Generated: 2026-11-22T17:23:29.542055+00:00
- Profile: `general` (General AI governance)

## Change summary

- Improved checks: 1
- Regressed checks: 10
- High-materiality regressions: 10
- Added statements: 5
- Removed statements: 11
- Modified statements: 3

## Material check changes

| Check | Previous | Current | Direction | Materiality |
|---|---|---|---|---|
| Explicit normative hierarchy or protected tier | `documented` | `absent` | `regressed` | `high` |
| Revision authority and approval process | `documented` | `asserted` | `regressed` | `high` |
| Stakeholder consultation or public-comment route | `documented` | `absent` | `regressed` | `high` |
| Scheduled review or reconsideration | `documented` | `asserted` | `regressed` | `high` |
| Defined revision triggers | `absent` | `asserted` | `improved` | `positive` |
| Prior-version retention and access | `documented` | `absent` | `regressed` | `high` |
| Rollback or suspension triggers | `documented` | `absent` | `regressed` | `high` |
| Rollback decision authority | `documented` | `absent` | `regressed` | `high` |
| Rollback exercise and effectiveness evidence | `documented` | `absent` | `regressed` | `high` |
| Advance notice to affected people | `documented` | `contradicted` | `regressed` | `high` |
| Independent review or oversight | `documented` | `absent` | `regressed` | `high` |

## Risk-warning movement

- New: The document appears to permit material changes without notice.

## Statement changes

| Type | Similarity | Previous source | Current source | Text |
|---|---:|---|---|---|
| `modified` | 0.98 | paragraph 4 | paragraph 4 | Previous: The alignment target is AI Constitution v1.0. → Current: The alignment target is AI Constitution v2.0. |
| `modified` | 0.90 | paragraph 14 | paragraph 9 | Previous: Users may appeal and request human review. → Current: Users may appeal and request internal human review. |
| `modified` | 0.95 | paragraph 2 | paragraph 2 | Previous: Version number: 1.0.0. → Current: Version number: 2.0.0. |
| `removed` | — | paragraph 7 | N/A | A 60-day public consultation is held before changing a core principle. |
| `removed` | — | paragraph 12 | N/A | A rollback drill is conducted every six months. |
| `removed` | — | paragraph 13 | N/A | Affected users receive 30 days advance notice before a material change. |
| `removed` | — | paragraph 16 | N/A | Audit logs are append-only and tamper-evident. |
| `removed` | — | paragraph 17 | N/A | Evidence is retained for seven years. |
| `removed` | — | paragraph 18 | N/A | Independent review is conducted by an external auditor. |
| `removed` | — | paragraph 9 | N/A | Previous versions remain available in a public archive. |
| `removed` | — | paragraph 11 | N/A | Rollback is approved by the Incident Commander. |
| `removed` | — | paragraph 10 | N/A | Rollback when a warning threshold or redline is breached. |
| `removed` | — | paragraph 5 | N/A | The policy is reviewed annually. |
| `removed` | — | paragraph 6 | N/A | The revision procedure requires approval by the AI Governance Board. |
| `added` | — | N/A | paragraph 11 | Audit logs are retained. |
| `added` | — | N/A | paragraph 12 | Independent review is provided by the management committee. |
| `added` | — | N/A | paragraph 5 | The company may revise the policy at any time without notice. |
| `added` | — | N/A | paragraph 8 | The company may suspend user access if controls fail. |
| `added` | — | N/A | paragraph 6 | The policy is reviewed when needed. |

## Claim boundary

This report compares two written versions using rule-based document evidence. It can identify declared changes, grade movement, and new warnings. It does not prove why a change was made, whether approval occurred, whether the change operated, or whether the revised system is safe or compliant.
