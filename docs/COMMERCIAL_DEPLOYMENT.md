# Commercial deployment

## Status

The v0.2.0 codebase contains a runnable single-node commercial API. It is ready
for controlled pilots and paid-service integration work, not for an uncontrolled
public launch.

Production launch still requires:

- an HTTPS domain and managed reverse proxy;
- encrypted disk or volume storage;
- a payment merchant account and processor adapter;
- privacy policy, terms, refund policy, tax treatment, and DPA templates reviewed
  for the operator's jurisdiction;
- database and report backups with tested restore procedures;
- monitoring, alerting, abuse handling, and a security review;
- capacity testing on representative 50–150 page reports.

## Data model

The service stores:

- organizations and plan limits;
- SHA-256 hashes of API keys;
- tenant-scoped job metadata;
- uploaded input files during processing;
- completed JSON reports until the retention deadline.

Plaintext API keys are returned once and are never stored. Input files are
deleted after processing. Reports are tenant-isolated and can be deleted by the
owning organization.

## Environment

| Variable | Purpose | Default |
|---|---|---|
| `ICS_SERVICE_DATA_DIR` | SQLite database, inputs, and reports | `.ics-crv-service` |
| `ICS_SERVICE_MAX_WORKERS` | In-process audit workers | `2` |
| `ICS_REPORT_RETENTION_DAYS` | Completed report retention | `7` |
| `ICS_BILLING_WEBHOOK_SECRET` | HMAC key for subscription events | unset |
| `ICS_STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | unset |
| `ICS_INLINE_WORKER` | Run jobs synchronously in tests | unset |
| `ICS_AUDIT_API_URL` | Plugin cloud API base URL | unset |
| `ICS_AUDIT_API_KEY` | Plugin cloud API key | unset |

Never put API keys or webhook secrets in the repository.

## Plans

| Plan | Monthly documents |
|---|---:|
| `trial` | 5 |
| `starter` | 25 |
| `pro` | 150 |
| `enterprise` | 10,000 |

The limits are code-level defaults and can be overridden administratively.
Commercial pricing should be set from measured processing cost and support
load, not only from document count.

## Billing webhook

Send JSON to `POST /v1/billing/webhook` and include:

```text
X-ICS-Timestamp: <unix seconds>
X-ICS-Signature: sha256=<hex HMAC-SHA256 of "<timestamp>." + raw request body>
```

Requests outside a five-minute clock window are rejected.

Example payload:

```json
{
  "organization_id": "org_...",
  "event": "subscription.activated",
  "plan": "pro"
}
```

Supported events:

- `subscription.activated`
- `subscription.updated`
- `subscription.cancelled`

The generic endpoint deliberately uses a provider-neutral signature. Paddle,
Lemon Squeezy, or another processor needs an adapter that verifies the
provider's native signature and translates its event into this payload. Stripe
can use the native endpoint below. Do not expose either webhook secret to
browser clients.

### Stripe-compatible endpoint

`POST /v1/billing/stripe-webhook` verifies the native
`Stripe-Signature: t=...,v1=...` header and accepts:

- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`

The Stripe object must include metadata:

```json
{
  "organization_id": "org_...",
  "plan": "starter"
}
```

For Checkout Sessions, `client_reference_id` may carry the organization ID.
Configure these fields in the processor's Payment Link, Checkout, or product
metadata before enabling the webhook.

## Scaling boundaries

The included worker uses an in-process thread pool and SQLite job table. This is
adequate for a pilot with one application process. Before horizontal scaling:

- move the queue to a durable external queue;
- claim jobs with a database lease or distributed lock;
- move reports to object storage with tenant-scoped encryption;
- replace local SQLite with PostgreSQL;
- run document parsing in isolated workers with CPU and memory limits;
- set per-tenant concurrency and total-page quotas.

## Minimum operating checks

```powershell
ics-crv-admin create-org --name "Pilot" --plan trial
ics-crv-admin issue-key --organization-id org_... --name pilot
ics-crv serve-commercial --host 127.0.0.1 --port 8766
```

Then verify:

- unauthenticated requests return 401;
- one audit consumes one quota unit;
- a failed parse refunds the quota unit;
- another organization cannot retrieve the report;
- report deletion removes the JSON file;
- webhook requests with an invalid signature return 401.

## Legal and claims boundary

Do not advertise the output as legal advice, assurance, certification,
compliance approval, investment advice, or proof that a company is not
greenwashing. The service audits written structure and evidence traceability.

Terms and privacy language must be reviewed by qualified counsel for the final
operator entity and target markets.
