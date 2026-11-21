# Commercial deployment

Status updated: 2026-11-21

## Current state

The v0.2.0 pilot is deployed on Cloudflare:

- Worker and HTTPS API:
  `https://ics-commitment-audit-api.franka328162810.workers.dev`
- D1: `ics-commitment-audit-db`
- Queue: `ics-commitment-audit-jobs`
- Dead-letter queue: `ics-commitment-audit-jobs-dlq`
- Private R2 bucket: `ics-commitment-audit-reports`
- Container application: `ics-commitment-audit-api-auditcontainer`
- Runtime image: `0.2.0-r2`

The API passes the current smoke, tenant-isolation, failure-refund, concurrency,
backup, and HTTPS checks. It is suitable for controlled pilots.

It is not yet a fully public paid launch because Stripe is not configured, the
legal pages have not received counsel review, alert delivery has not been
verified, and large-document concurrency has not been tested at production
scale.

## Public endpoints

```text
GET    /
GET    /privacy
GET    /terms
GET    /v1/health
POST   /v1/audits
GET    /v1/audits/{job_id}
GET    /v1/audits/{job_id}/report
DELETE /v1/audits/{job_id}
GET    /v1/account
POST   /v1/billing/checkout
POST   /v1/billing/stripe-webhook
POST   /v1/billing/webhook
POST   /v1/admin/organizations
POST   /v1/admin/audits/{job_id}/stop
```

All tenant endpoints require `Authorization: Bearer <API key>`. Admin endpoints
require `X-ICS-Admin-Token`.

## Data handling

- API keys are returned once and stored as SHA-256 hashes.
- D1 contains organizations, key hashes, job metadata, and billing event IDs.
- R2 contains source uploads only while a job is being processed and completed
  report JSON afterward.
- Original uploads are deleted after success or final failure.
- Reports expire after seven days.
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
| `pro` | 150 |
| `enterprise` | 10,000 |

The values are enforced maxima, not product prices. Do not publish a retail
price until measured infrastructure cost, Stripe fees, tax treatment, customer
support, and the value of the report have been reviewed together.

## Required secrets

| Name | Current state | Purpose |
|---|---|---|
| `ICS_ADMIN_TOKEN` | configured | Provision organizations and stop audit containers |
| `ICS_INTERNAL_TOKEN` | configured | Worker-to-container authentication |
| `ICS_STRIPE_WEBHOOK_SECRET` | blocked | Verify native Stripe webhooks |
| `STRIPE_SECRET_KEY` | blocked | Create Stripe Checkout Sessions |
| `STRIPE_PRICE_STARTER` | blocked | Starter subscription Price ID |
| `STRIPE_PRICE_PRO` | blocked | Pro subscription Price ID |

Never commit `.dev.vars`, local service records, API keys, Stripe credentials,
or exported customer reports.

Set secrets with:

```powershell
wrangler secret put ICS_STRIPE_WEBHOOK_SECRET
wrangler secret put STRIPE_SECRET_KEY
wrangler secret put STRIPE_PRICE_STARTER
wrangler secret put STRIPE_PRICE_PRO
```

## Stripe activation

The code at `POST /v1/billing/checkout` creates a subscription Checkout Session
for an authenticated organization. Until Stripe is configured, it correctly
returns `503` instead of issuing a fake payment link.

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

Recovery drill performed on 2026-11-21:

- D1 export downloaded successfully.
- SQL imported into a new local SQLite database.
- The restored database contained all expected tables and rows.
- Export size: 4,845 bytes at test time.

Store production exports in encrypted private storage, restrict access, and
test a restore into a separate D1 database before relying on the backup.

## Monitoring

Workers Logs and Container logs are enabled at 100% sampling.

```powershell
npx wrangler tail --status error
```

No external alert destination has been verified. Before paid launch, configure:

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

- malformed PDF returned a clean container `400` on the first attempt;
- the failed job refunded its quota unit;
- cross-tenant report access and deletion returned `404`;
- completed report retrieval returned `200` with evidence;
- the source object was removed from R2 after successful processing;
- completed report deletion returned `204` and removed the object.

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

## Launch blockers

- Complete Stripe onboarding and create Starter/Pro Price IDs.
- Review privacy, terms, refund, tax, and data-processing language.
- Configure and test external alerts.
- Test representative 50-150 page Chinese and English PDFs at expected peak
  concurrency.
- Set retail prices from measured unit economics.
- Obtain an independent evaluation if customers require assurance-grade
  validation rather than single-reviewer internal validation.

## Claims boundary

The service audits written commitment structure and evidence traceability. It
does not determine whether a company is truthful, greenwashing, compliant,
assured, or performing well. Do not market it as legal advice, audit assurance,
certification, investment advice, or proof of misconduct.
