# Go-to-market and payment operations

This note describes a practical first launch path for an international,
English-first customer base. It separates customer acquisition, payment flow,
and the seller's responsibilities.

## Initial buyers

Start with narrow, evidence-driven segments:

1. Independent sustainability and ESG consultants serving small or mid-sized
   companies.
2. Corporate sustainability analysts who review public reports and need an
   evidence matrix before human review.
3. Researchers and policy analysts comparing climate commitments across firms.
4. Procurement or due-diligence teams that need structured questions and source
   citations.

Do not lead with claims of assurance, compliance certification, or greenwashing
detection. Lead with faster evidence extraction, consistent structure checks,
and traceable source locations.

## How real users find the product

Use a narrow set of owned and targeted channels before spending on advertising.

### 1. GitHub as the technical storefront

- Keep the repository README focused on the customer problem, a visible sample,
  validation limits, the purchase link, and a three-step start path.
- Publish a customer guide and methodology so buyers can evaluate the rules
  before paying.
- Use precise GitHub topics such as `esg`, `climate`, `sustainability-reporting`,
  `commitment-audit`, `document-analysis`, and `crv`.
- Create a release with a short changelog and link it back to the product page.

### 2. ICS website

Add a product page on `ics-studies.org` that includes:

- one concrete example commitment and its evidence;
- a sample redacted JSON/HTML report;
- supported inputs and explicit exclusions;
- the Gumroad purchase button;
- links to methodology, privacy, terms, support, and refund policy.

### 3. Targeted outreach

Build a list of 50–100 relevant people rather than mass-emailing. Prioritize
consultants, researchers, and sustainability analysts who publicly discuss
commitment quality or annual-report review.

Useful outreach sequence:

1. Send one short note explaining the exact workflow and a sample finding.
2. Offer to audit one public report and return a redacted example.
3. Ask whether the output saves review time or is missing a decision-relevant
   field.
4. Request a paid founding subscription only after the workflow is understood.

### 4. Content and search

Publish practical pages that answer real tasks:

- “How to extract climate commitments with page-level evidence.”
- “A checklist for observable, enforceable, and revisable climate targets.”
- “What a commitment can say when it lacks a baseline, owner, or remedy.”
- “How to compare climate target wording across annual reports.”

Avoid claiming that the tool certifies compliance or determines truth. Use
examples, methodology, and limitations to build trust.

### 5. Partners and communities

Approach small ESG consultancies, academic groups, reporting teams, and
newsletter authors with a revenue share or white-label discussion only after the
core product is stable. Communities matter more than broad advertising at this
stage.

## Payment flow

```text
Buyer finds the product page
        ↓
Gumroad checkout and tax calculation
        ↓
Gumroad issues a license key
        ↓
Buyer activates at /activate
        ↓
ICS API creates one organization and API key
        ↓
Gumroad membership status is checked every 15 minutes
        ↓
Gumroad pays the seller through the configured PayPal payout method
```

The customer never sends card data to ICS. Gumroad handles checkout, payment
method collection, receipts, subscription renewal, and the configured payout.

## What the seller must do

### Before accepting payment

- Confirm the PayPal payout email in Gumroad Settings → Payments.
- Log in directly at `paypal.com` and confirm the same email, legal name, payout
  eligibility, currency, and account restrictions.
- Keep the PayPal account verified and able to receive USD.
- Review the privacy page, terms, refund language, and local tax obligations.
- Keep support email and Gumroad notifications monitored.

### During operations

- Respond to customers about activation, failed files, refunds, and privacy.
- Check Gumroad for cancelled memberships, failed renewals, disputes, and
  refunds.
- Monitor the public health page and GitHub Actions production-health workflow.
- Review monthly document demand and Cloudflare cost.
- Keep API keys, license keys, and customer documents private.
- Reconcile Gumroad sales with PayPal payouts and business accounting records.

### When the first sale occurs

1. Confirm the Gumroad sale and license issuance.
2. Watch the customer activate the license and make the first audit.
3. Check for repeatable extraction or onboarding failures.
4. Confirm the sale appears in the Gumroad balance and payout report.
5. After the payout threshold is reached, verify the payout in Gumroad and the
   matching receipt in PayPal.

## Current payout facts observed in the account

The seller account currently shows:

- payout method: PayPal;
- seller country: China;
- minimum payout threshold: US$100;
- PayPal payout fee: 2%;
- payouts not paused.

These platform settings can change. Recheck Gumroad and PayPal before each
payout cycle.

## First-30-days target

Do not optimize for raw traffic yet. Measure:

- 50–100 targeted visits;
- 10 product-guide reads;
- 3 substantive customer conversations;
- 1–3 paid founding subscriptions;
- successful activation and first-audit completion for every buyer;
- zero unresolved payout or access failures.

The next product investment should be driven by observed documents and support
friction, not by adding more plans or features.
