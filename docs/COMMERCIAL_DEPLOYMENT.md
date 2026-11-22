# Commercial deployment

Status updated: 2026-11-22

## Current state

The v0.3.1 pilot is deployed on Cloudflare:

- Worker and HTTPS API:
  `https://ics-commitment-audit-api.franka328162810.workers.dev`
- D1: `ics-commitment-audit-db`
- Queue: `ics-commitment-audit-jobs`
- Dead-letter queue: `ics-commitment-audit-jobs-dlq`
- Private R2 bucket: `ics-commitment-audit-reports`
- Container application: `ics-commitment-audit-api-auditcontainer`
- Runtime image: `0.3.1-r1`

The API passes the current smoke, tenant-isolation, failure-refund, concurrency,
backup, HTTPS, 100-page boundary, and quota-refund checks. The v0.3.1 release
also passed production checks for both audit modes, the browser workbench, and
the dedicated Recursive Freedom product page.

The Gumroad product is published at:

```text
https://icsstudies.gumroad.com/l/ics-commitment-audit
```

Gumroad first published the product on 2026-11-22. The owner-only test purchase
completed without a charge, its license key activated successfully, and D1
contains a test `founding-team` organization with 100 monthly documents,
`active=1`, `billing_provider=gumroad`, and `billing_status=active`.

The legal pages have not received independent counsel review. GitHub Actions
now probes public availability every 15 minutes, but a separate external alert
destination has not been verified end to end.

## Public endpoints

```text
GET    /
GET    /activate
GET    /workspace
GET    /recursive-freedom
GET    /recursive-freedom/sample
GET    /privacy
GET    /terms
GET    /v1/health
POST   /v1/audits
GET    /v1/audits/{job_id}
GET    /v1/audits/{job_id}/report
DELETE /v1/audits/{job_id}
GET    /v1/account
POST   /v1/billing/gumroad/redeem
POST   /v1/billing/checkout
POST   /v1/billing/stripe-webhook
POST   /v1/billing/webhook
POST   /v1/admin/organizations
POST   /v1/admin/audits/{job_id}/stop
```

All tenant endpoints require `Authorization: Bearer <API key>`. Admin endpoints
require `X-ICS-Admin-Token`.

`POST /v1/audits` accepts `X-ICS-Mode: commitment` for ESG/climate reports or
`X-ICS-Mode: recursive-freedom` for Recursive Freedom Audit for AI. Both
modes share the same quota and document limits.

## Data handling

- API keys are returned once and stored as SHA-256 hashes.
- D1 contains organizations, key hashes, job metadata, and billing event IDs.
- R2 contains source uploads only while a job is being processed and completed
  report JSON afterward.
- Original uploads are deleted after success or final failure.
- Reports expire after seven days.
- Gumroad license keys are verified with Gumroad, encrypted with AES-GCM before
  being stored in D1, and never returned by an API endpoint.
- Terminal job metadata is deleted after 180 days.
- An R2 lifecycle rule expires any remaining `orgs/` object after 30 days and
  aborts incomplete multipart uploads after one day.
- Reports are private and are served only through a tenant-authenticated API.

The 180-day metadata retention is a policy target implemented by the daily cron.
The current deployment has less than 180 days of production data, so no
production-age deletion event has yet been observed.

## Plans

| Plan | Monthly documents |
|---|---:|
| `trial` | 5 |
| `starter` | 25 |
| `founding-team` | 100 |
| `pro` | 150 |
| `enterprise` | 10,000 |

Pricing, tax presentation, refunds, and customer support are handled by
Gumroad for the current paid pilot. The product is `$29/month`, capped at 20
active founding supporters. A document may contain at most 100 pages and 50 MB.

## Required secrets

| Name | Current state | Purpose |
|---|---|---|
| `ICS_ADMIN_TOKEN` | configured | Provision organizations and stop audit containers |
| `ICS_INTERNAL_TOKEN` | configured | Worker-to-container authentication |
| `ICS_GUMROAD_ENCRYPTION_KEY` | configured | AES-GCM protection for stored Gumroad license keys |
| `ICS_STRIPE_WEBHOOK_SECRET` | blocked | Verify native Stripe webhooks |
| `STRIPE_SECRET_KEY` | blocked | Create Stripe Checkout Sessions |
| `STRIPE_PRICE_STARTER` | blocked | Starter subscription Price ID |
| `STRIPE_PRICE_PRO` | blocked | Pro subscription Price ID |

Never commit `.dev.vars`, local service records, API keys, Stripe credentials,
or exported customer reports.

Set secrets with:

```powershell
wrangler secret put ICS_GUMROAD_ENCRYPTION_KEY
wrangler secret put ICS_STRIPE_WEBHOOK_SECRET
wrangler secret put STRIPE_SECRET_KEY
wrangler secret put STRIPE_PRICE_STARTER
wrangler secret put STRIPE_PRICE_PRO
```

## Gumroad activation

The production checkout route is Gumroad, not Stripe. A successful purchase
issues a Gumroad license key. The customer enters that key at `/activate`; the
Worker calls Gumroad's license verification API with
`increment_uses_count=false`, rejects refunds, disputes, chargebacks, ended
memberships, cancellations, and failed renewals, and then creates:

- one `founding-team` organization;
- one 100-document monthly quota;
- one shared API key displayed only once.

A license hash and encrypted license value are stored in D1 to prevent reuse
and support ongoing status checks. The billing cron runs every 15 minutes and
rechecks at most 20 organizations, matching the founding cap. Daily maintenance
retains reports for seven days and removes terminal job metadata after 180 days.

Before publishing the Gumroad listing, use Gumroad's logged-in test-purchase
flow. Do not pay with a real card or attempt an actual self-purchase. Complete
the test purchase, copy its license key, activate it through `/activate`, and
verify the returned plan, 100-document limit, and one-time API key.

## Legacy Stripe path

The code at `POST /v1/billing/checkout` can create a subscription Checkout
Session for an authenticated organization. It is retained as an optional future
route and returns `503` until fully configured. It is not used by the current
Gumroad pilot.

Activation still requires the account owner to complete:

1. Stripe identity and business verification.
2. Tax and payout details.
3. Starter and Pro recurring products/prices.
4. A webhook endpoint pointing to
   `POST /v1/billing/stripe-webhook`.
5. Webhook events for checkout and subscription lifecycle.
6. Test-mode checkout, cancellation, upgrade/downgrade, and refund tests.
7. Switching to live credentials only after the test-mode matrix passes.

Checkout metadata must carry `organization_id` and `plan`. The Worker also
copies those values into subscription metadata so cancellation events retain
the tenant association.

## Deployment

```powershell
cd cloudflare
npm ci
npx wrangler types
npx tsc --noEmit
npx wrangler deploy --dry-run
npx wrangler deploy
```

The current `wrangler.jsonc` points to the prebuilt Cloudflare Registry image.
For a normal application-only update, build a child image or rebuild from the
repository Dockerfile, publish a new immutable tag, update `wrangler.jsonc`, and
deploy. Do not overwrite a production image tag without a rollout plan.

## Backup and recovery

Cloudflare D1 includes Time Travel for the paid retention window. In addition,
run an export before schema changes and at least weekly:

```powershell
npx wrangler d1 export ics-commitment-audit-db --remote --output backup.sql
```

Recovery drill performed on 2026-11-22:

- D1 export downloaded successfully.
- SQL imported into a new local SQLite database.
- The restored database contained all expected tables and rows.
- Export size: 13,437 bytes at test time.
- Integrity check: `ok`.
- Restored rows: 4 organizations, 3 API keys, 13 audit jobs, 0 billing events.

A second D1 export was made immediately before the v0.3.0 `audit_mode`
migration. It is stored only in the Git-ignored local private backup directory:

- export size: 16,370 bytes;
- SHA-256: `F4D27B085D4A6F9D89A095C055A9479EBEA91D37A13C6E0EEF7042F7E3F37D4B`;
- migration applied successfully after export;
- all 16 pre-existing jobs were backfilled to `commitment`.

Store production exports in encrypted private storage, restrict access, and
test a restore into a separate D1 database before relying on the backup.

## Monitoring

Workers Logs and Container logs are enabled at 100% sampling.

```powershell
npx wrangler tail --status error
```

`.github/workflows/production-health.yml` probes `/v1/health` and `/activate`
every 15 minutes and fails the GitHub job when either endpoint is unavailable.
A failed scheduled job is visible in the repository's Actions page and can
trigger the repository owner's GitHub notification settings. Before or
immediately after the first paid customer, also configure:

- HTTPS uptime checks for `/v1/health`;
- Worker 5xx and Queue/DLQ alerts;
- elevated container startup failure alerts;
- D1 and R2 error-rate alerts;
- a notification channel that is tested end to end.

The initial 403 produced by a Python default User-Agent showed that Cloudflare
edge automation rules can affect machine clients. Maintain an explicit product
User-Agent and a compatibility smoke test for every supported SDK.

## Validation record

The final load check on 2026-11-21 produced:

| Check | Result |
|---|---:|
| Health requests | 30/30 successful |
| Health p50 | 848.07 ms |
| Health p95 | 1,930.93 ms |
| Concurrent audits | 3/3 successful |
| Audit end-to-end p50 | 17,733.22 ms |
| Audit end-to-end p95 | 23,854.35 ms |

The first concurrency run had only 2/3 successes because two idle containers
occupied `max_instances=2` for five minutes. The runtime was corrected to use
four maximum instances and a 60-second inactivity timeout. The repeated run
passed 3/3.

Additional checks:

- AI policy mode returned ten checks with a decoded source filename;
- both modes consumed exactly one quota unit each;
- a 101-page PDF in the new mode was rejected with `413` and refunded;
- cross-tenant access to the new mode job returned `404`;
- temporary production-test organizations and keys were removed after the run;
- 101-page synthetic PDF was rejected with the explicit 100-page limit and
  refunded its quota unit.
- A synthetic text-layer PDF completed, returned a report, and consumed exactly
  one quota unit.
- malformed PDF returned a clean container `400` on the first attempt;
- the failed job refunded its quota unit;
- cross-tenant report access and deletion returned `404`;
- completed report retrieval returned `200` with evidence;
- the source object was removed from R2 after successful processing;
- completed report deletion returned `204` and removed the object.

## Recursive Freedom Audit validation

The v0.2 AI-policy rule set was tested against five public policies or
governance documents:

- OpenAI Usage Policies;
- Anthropic Usage Policy;
- Google Generative AI Prohibited Use Policy;
- Anthropic Responsible Scaling Policy;
- Google DeepMind's introduction to the Frontier Safety Framework.

The development benchmark contains 50 check-level decisions. The current rules
and Codex-assisted written adjudication agree on all 50. Nineteen checks were
expected to be present or partial; all 19 were detected, with zero recorded
false positives and zero recorded false negatives in this development set.

This is not independent external validation. The rules were refined after
reviewing initial false positives, so the benchmark is not a fully held-out
test. The public product page and `docs/RECURSIVE_FREEDOM_AUDIT.md` state that
limitation.

## Cost basis

Cloudflare pricing checked 2026-11-13:

- Workers Paid: USD 5 per month.
- `standard-1`: 0.5 vCPU, 4 GiB memory, 8 GB disk.
- Included monthly: 25 GiB-hours memory, 375 vCPU-minutes, and 200 GB-hours
  disk.
- Additional memory: USD 0.0000025 per GiB-second.
- Additional active CPU: USD 0.000020 per vCPU-second.
- Additional disk: USD 0.00000007 per GB-second.
- APAC container egress: USD 0.04 per GB after the included allotment.

For a small job that keeps a `standard-1` instance active for a conservative
90 seconds and uses the full 0.5 vCPU, the upper-bound container compute charge
is approximately USD 0.0018 before monthly included usage. CPU is billed only
while active, so the normal charge should be lower. This estimate excludes
Workers, D1, R2, Queue, logs, and payment fees.

The memory allowance alone covers roughly 250 conservative 90-second runs per
month. Recalculate after observing larger real reports; page count, OCR, and
document complexity can move CPU and duration materially.

## Remaining launch risks

- Have privacy, terms, refund, tax, and data-processing language reviewed for
  the seller's jurisdiction and customer markets.
- Configure and test external alerts.
- Authenticate the separate `cf` billing CLI with Billing Edit permission and
  verify the Workers spend policy. A Workers limit does not cap Containers,
  Durable Objects, D1, R2, Queues, or other separately billed products.
- Test representative 50-100 page Chinese and English PDFs at expected peak
  concurrency.
- Obtain an independent evaluation if customers require assurance-grade
  validation rather than single-reviewer internal validation.

## Claims boundary

The service audits written commitment structure and evidence traceability. It
does not determine whether a company is truthful, greenwashing, compliant,
assured, or performing well. Do not market it as legal advice, audit assurance,
certification, investment advice, or proof of misconduct.
