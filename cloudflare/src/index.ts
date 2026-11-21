import { DurableObject } from "cloudflare:workers";
import {
  htmlResponse,
  landingPage,
  privacyPage,
  termsPage,
} from "./public-pages";

const CONTAINER_PORT = 8080;
const INACTIVITY_TIMEOUT_MS = 60 * 1000;
const MAX_JSON_BODY_BYTES = 64 * 1024;
const NON_RETRYABLE_CONTAINER_STATUSES = new Set([400, 413, 415, 422]);
const PLAN_LIMITS = {
  trial: 5,
  starter: 25,
  pro: 150,
  enterprise: 10_000,
} as const;
type Plan = keyof typeof PLAN_LIMITS;

interface Organization {
  id: string;
  name: string;
  plan: Plan;
  monthly_document_limit: number;
  documents_used: number;
  usage_period: string;
  active: number;
}

interface AuditJob {
  id: string;
  organization_id: string;
  status: string;
  filename: string;
  content_type: string;
  byte_count: number;
  upload_key: string;
  report_key: string | null;
  weights: string;
  error: string | null;
  attempts: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

interface QueueJob {
  job_id: string;
}

const jsonHeaders = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
  "referrer-policy": "no-referrer",
};

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: jsonHeaders,
  });
}

function nowIso(): string {
  return new Date().toISOString();
}

function currentPeriod(): string {
  return new Date().toISOString().slice(0, 7);
}

function cleanFilename(raw: string | null): string | null {
  if (!raw) return null;
  let decoded: string;
  try {
    decoded = decodeURIComponent(raw);
  } catch {
    return null;
  }
  const filename = decoded.split(/[\\/]/).pop()?.trim() ?? "";
  if (
    !filename ||
    filename.length > 180 ||
    /[\u0000-\u001f\u007f]/.test(filename) ||
    !/\.(pdf|docx|txt|md|markdown)$/i.test(filename)
  ) {
    return null;
  }
  return filename;
}

function bytesToHex(bytes: Uint8Array): string {
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
}

function bytesToBase64Url(bytes: Uint8Array): string {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/g, "");
}

async function sha256Hex(value: string): Promise<string> {
  const digest = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(value),
  );
  return bytesToHex(new Uint8Array(digest));
}

function textToBase64Url(value: string): string {
  return bytesToBase64Url(new TextEncoder().encode(value));
}

async function hmacHex(secret: string, value: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign(
    "HMAC",
    key,
    new TextEncoder().encode(value),
  );
  return bytesToHex(new Uint8Array(signature));
}

async function timingSafeEqual(left: string, right: string): Promise<boolean> {
  const leftHash = new Uint8Array(
    await crypto.subtle.digest("SHA-256", new TextEncoder().encode(left)),
  );
  const rightHash = new Uint8Array(
    await crypto.subtle.digest("SHA-256", new TextEncoder().encode(right)),
  );
  let difference = 0;
  for (let index = 0; index < leftHash.length; index += 1) {
    difference |= leftHash[index] ^ rightHash[index];
  }
  return difference === 0;
}

async function authenticate(request: Request, env: Env): Promise<Organization | null> {
  const authorization = request.headers.get("authorization") ?? "";
  const match = /^Bearer\s+(.+)$/i.exec(authorization);
  if (!match) return null;
  const keyHash = await sha256Hex(match[1]);
  return env.DB.prepare(
    `SELECT o.*
       FROM api_keys AS k
       JOIN organizations AS o ON o.id = k.organization_id
      WHERE k.key_hash = ? AND k.revoked_at IS NULL AND o.active = 1`,
  )
    .bind(keyHash)
    .first<Organization>();
}

async function requireAdmin(request: Request, env: Env): Promise<boolean> {
  const supplied = request.headers.get("x-ics-admin-token") ?? "";
  return (
    Boolean(env.ICS_ADMIN_TOKEN) &&
    Boolean(supplied) &&
    (await timingSafeEqual(supplied, env.ICS_ADMIN_TOKEN))
  );
}

async function reserveJob(
  env: Env,
  organizationId: string,
  jobId: string,
  filename: string,
  contentType: string,
  byteCount: number,
  uploadKey: string,
  weights: string,
): Promise<boolean> {
  const period = currentPeriod();
  const createdAt = nowIso();
  const results = await env.DB.batch([
    env.DB.prepare(
      `UPDATE organizations
          SET documents_used = CASE
                WHEN usage_period = ? THEN documents_used + 1
                ELSE 1
              END,
              usage_period = ?
        WHERE id = ?
          AND active = 1
          AND CASE
                WHEN usage_period = ? THEN documents_used < monthly_document_limit
                ELSE 1
              END`,
    ).bind(period, period, organizationId, period),
    env.DB.prepare(
      `INSERT INTO audit_jobs
        (id, organization_id, status, filename, content_type, byte_count,
         upload_key, weights, created_at)
       SELECT ?, ?, 'queued', ?, ?, ?, ?, ?, ?
        WHERE changes() = 1`,
    ).bind(
      jobId,
      organizationId,
      filename,
      contentType,
      byteCount,
      uploadKey,
      weights,
      createdAt,
    ),
  ]);
  return (
    Number(results[0]?.meta.changes ?? 0) === 1 &&
    Number(results[1]?.meta.changes ?? 0) === 1
  );
}

async function refundReservation(
  env: Env,
  jobId: string,
  message: string,
): Promise<void> {
  await env.DB.batch([
    env.DB.prepare(
      `UPDATE audit_jobs
          SET status = 'failed', error = ?, completed_at = ?
        WHERE id = ? AND status IN ('queued', 'running')`,
    ).bind(message.slice(0, 2000), nowIso(), jobId),
    env.DB.prepare(
      `UPDATE organizations
          SET documents_used = MAX(0, documents_used - 1)
        WHERE id = (SELECT organization_id FROM audit_jobs WHERE id = ?)
          AND changes() = 1`,
    ).bind(jobId),
  ]);
}

function jobPayload(job: AuditJob): Record<string, unknown> {
  return {
    id: job.id,
    status: job.status,
    filename: job.filename,
    byte_count: job.byte_count,
    weights: job.weights,
    error: job.error,
    attempts: job.attempts,
    created_at: job.created_at,
    started_at: job.started_at,
    completed_at: job.completed_at,
  };
}

async function callContainer(
  env: Env,
  job: AuditJob,
  body: ReadableStream,
): Promise<Response> {
  const container = env.AUDIT_CONTAINER.getByName(job.id);
  return container.fetch(
    new Request("http://container/audit", {
      method: "POST",
      headers: {
        "content-type": job.content_type,
        "x-ics-filename": encodeURIComponent(job.filename),
        "x-ics-weights": job.weights,
        "x-ics-internal-token": env.ICS_INTERNAL_TOKEN,
      },
      body,
    }),
  );
}

async function processQueueMessage(
  message: Message<QueueJob>,
  env: Env,
): Promise<void> {
  const jobId = message.body.job_id;
  const job = await env.DB.prepare("SELECT * FROM audit_jobs WHERE id = ?")
    .bind(jobId)
    .first<AuditJob>();
  if (!job || ["completed", "failed", "cancelled"].includes(job.status)) {
    message.ack();
    return;
  }
  await env.DB.prepare(
    `UPDATE audit_jobs
        SET status = 'running', started_at = COALESCE(started_at, ?),
            attempts = attempts + 1, error = NULL
      WHERE id = ?`,
  )
    .bind(nowIso(), jobId)
    .run();
  const upload = await env.REPORTS.get(job.upload_key);
  if (!upload?.body) {
    if (message.attempts >= 3) {
      await refundReservation(env, jobId, "Uploaded source file was not found");
    } else {
      await env.DB.prepare(
        "UPDATE audit_jobs SET status = 'queued', error = ? WHERE id = ?",
      )
        .bind("Uploaded source file was not found", jobId)
        .run();
    }
    message.retry({ delaySeconds: Math.min(120, 30 * message.attempts) });
    return;
  }
  try {
    const response = await callContainer(env, job, upload.body);
    if (!response.ok) {
      const detail = (await response.text()).slice(0, 1000);
      if (NON_RETRYABLE_CONTAINER_STATUSES.has(response.status)) {
        await refundReservation(
          env,
          jobId,
          `Container returned ${response.status}: ${detail}`,
        );
        await env.REPORTS.delete(job.upload_key);
        message.ack();
        return;
      }
      throw new Error(`Container returned ${response.status}: ${detail}`);
    }
    const reportBody = await response.text();
    JSON.parse(reportBody);
    const reportKey = `orgs/${job.organization_id}/reports/${job.id}.json`;
    await env.REPORTS.put(reportKey, reportBody, {
      httpMetadata: { contentType: "application/json; charset=utf-8" },
      customMetadata: { organization_id: job.organization_id, job_id: job.id },
    });
    await env.DB.prepare(
      `UPDATE audit_jobs
          SET status = 'completed', report_key = ?, completed_at = ?, error = NULL
        WHERE id = ?`,
    )
      .bind(reportKey, nowIso(), jobId)
      .run();
    await env.REPORTS.delete(job.upload_key);
    message.ack();
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    if (message.attempts >= 3) {
      await refundReservation(env, jobId, detail);
      await env.REPORTS.delete(job.upload_key);
    } else {
      await env.DB.prepare(
        "UPDATE audit_jobs SET status = 'queued', error = ? WHERE id = ?",
      )
        .bind(detail.slice(0, 2000), jobId)
        .run();
    }
    message.retry({ delaySeconds: Math.min(120, 30 * message.attempts) });
  }
}

function parseStripeSignature(header: string): {
  timestamp: string;
  signatures: string[];
} {
  const values = new Map<string, string[]>();
  for (const part of header.split(",")) {
    const [key, ...rest] = part.split("=");
    if (!key || rest.length === 0) continue;
    values.set(key, [...(values.get(key) ?? []), rest.join("=")]);
  }
  return {
    timestamp: values.get("t")?.[0] ?? "",
    signatures: values.get("v1") ?? [],
  };
}

async function verifyStripe(
  request: Request,
  body: string,
  secret: string,
): Promise<{ valid: boolean; event: Record<string, unknown> | null }> {
  const { timestamp, signatures } = parseStripeSignature(
    request.headers.get("stripe-signature") ?? "",
  );
  if (!timestamp || !/^\d+$/.test(timestamp)) return { valid: false, event: null };
  if (Math.abs(Math.floor(Date.now() / 1000) - Number(timestamp)) > 300) {
    return { valid: false, event: null };
  }
  const expected = await hmacHex(secret, `${timestamp}.${body}`);
  const valid = await Promise.all(
    signatures.map((signature) => timingSafeEqual(signature, expected)),
  ).then((matches) => matches.some(Boolean));
  if (!valid) return { valid: false, event: null };
  try {
    return { valid: true, event: JSON.parse(body) as Record<string, unknown> };
  } catch {
    return { valid: true, event: null };
  }
}

async function verifyGenericWebhook(
  request: Request,
  body: string,
  secret: string,
): Promise<boolean> {
  const timestamp = request.headers.get("x-ics-timestamp") ?? "";
  const signature = (request.headers.get("x-ics-signature") ?? "").replace(
    /^sha256=/,
    "",
  );
  if (!timestamp || !/^\d+$/.test(timestamp)) return false;
  if (Math.abs(Math.floor(Date.now() / 1000) - Number(timestamp)) > 300) {
    return false;
  }
  const expected = await hmacHex(secret, `${timestamp}.${body}`);
  return timingSafeEqual(signature, expected);
}

function sanitizePlan(value: unknown): Plan | null {
  return typeof value === "string" && value in PLAN_LIMITS ? (value as Plan) : null;
}

export class AuditContainer extends DurableObject<Env> {
  private starting: Promise<void> | undefined;

  constructor(ctx: DurableObjectState, env: Env) {
    super(ctx, env);
    if (ctx.container?.running) {
      void ctx.blockConcurrencyWhile(() =>
        ctx.container!.setInactivityTimeout(INACTIVITY_TIMEOUT_MS),
      );
    }
  }

  override async fetch(request: Request): Promise<Response> {
    this.starting ??= this.startAndWaitForPort().finally(() => {
      this.starting = undefined;
    });
    await this.starting;
    const url = new URL(request.url);
    url.protocol = "http:";
    url.host = "container";
    const forwarded = new Request(url, request);
    forwarded.headers.delete("host");
    return this.ctx.container!.getTcpPort(CONTAINER_PORT).fetch(forwarded);
  }

  async stopContainer(): Promise<boolean> {
    if (!this.ctx.container?.running) return false;
    await this.ctx.container.destroy("Stopped by ICS audit lifecycle control");
    return true;
  }

  private async startAndWaitForPort(): Promise<void> {
    const container = this.ctx.container;
    if (!container) throw new Error("Container binding is unavailable");
    if (!container.running) {
      container.start({
        enableInternet: false,
        env: { ICS_INTERNAL_TOKEN: this.env.ICS_INTERNAL_TOKEN },
      });
    }
    await container.setInactivityTimeout(INACTIVITY_TIMEOUT_MS);
    const port = container.getTcpPort(CONTAINER_PORT);
    for (let attempt = 0; attempt < 100; attempt += 1) {
      try {
        const response = await port.fetch("http://container/health", {
          signal: AbortSignal.timeout(1000),
        });
        await response.body?.cancel();
        if (response.ok) return;
      } catch {
        // The port may not yet be listening while the image starts.
      }
      await scheduler.wait(200);
    }
    throw new Error("Container did not become ready on port 8080");
  }

}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";
    if (request.method === "GET" && path === "/") {
      return htmlResponse(landingPage);
    }
    if (request.method === "GET" && path === "/privacy") {
      return htmlResponse(privacyPage);
    }
    if (request.method === "GET" && path === "/terms") {
      return htmlResponse(termsPage);
    }
    if (path === "/v1/health" && request.method === "GET") {
      await env.DB.prepare("SELECT 1").first();
      return json({ status: "ok", service: env.SERVICE_NAME, region: request.cf?.colo });
    }

    if (path === "/v1/admin/organizations" && request.method === "POST") {
      if (!(await requireAdmin(request, env))) {
        return json({ error: "Admin authorization required" }, 401);
      }
      const contentLength = Number(request.headers.get("content-length") ?? "0");
      if (contentLength > MAX_JSON_BODY_BYTES) {
        return json({ error: "Admin payload is too large" }, 413);
      }
      let payload: Record<string, unknown>;
      try {
        payload = (await request.json()) as Record<string, unknown>;
      } catch {
        return json({ error: "Invalid JSON" }, 400);
      }
      const name = typeof payload.name === "string" ? payload.name.trim() : "";
      const plan = sanitizePlan(payload.plan ?? "trial");
      if (!name || name.length > 160 || !plan) {
        return json({ error: "name and valid plan are required" }, 400);
      }
      const organizationId = `org_${crypto.randomUUID().replaceAll("-", "")}`;
      const keyId = `key_${crypto.randomUUID().replaceAll("-", "")}`;
      const tokenBytes = crypto.getRandomValues(new Uint8Array(32));
      const apiKey = `ics_live_${bytesToBase64Url(tokenBytes)}`;
      const keyHash = await sha256Hex(apiKey);
      const createdAt = nowIso();
      await env.DB.batch([
        env.DB.prepare(
          `INSERT INTO organizations
            (id, name, plan, monthly_document_limit, documents_used,
             usage_period, active, created_at)
           VALUES (?, ?, ?, ?, 0, ?, 1, ?)`,
        ).bind(
          organizationId,
          name,
          plan,
          PLAN_LIMITS[plan],
          currentPeriod(),
          createdAt,
        ),
        env.DB.prepare(
          `INSERT INTO api_keys
            (id, organization_id, name, key_hash, prefix, created_at)
           VALUES (?, ?, 'initial', ?, ?, ?)`,
        ).bind(keyId, organizationId, keyHash, apiKey.slice(0, 16), createdAt),
      ]);
      return json(
        {
          organization_id: organizationId,
          plan,
          monthly_document_limit: PLAN_LIMITS[plan],
          api_key_id: keyId,
          api_key: apiKey,
        },
        201,
      );
    }

    const adminStopMatch = /^\/v1\/admin\/audits\/([^/]+)\/stop$/.exec(path);
    if (adminStopMatch && request.method === "POST") {
      if (!(await requireAdmin(request, env))) {
        return json({ error: "Admin authorization required" }, 401);
      }
      const stopped = await env.AUDIT_CONTAINER.getByName(
        adminStopMatch[1],
      ).stopContainer();
      return json({ stopped });
    }

    if (path === "/v1/billing/stripe-webhook" && request.method === "POST") {
      const secret = env.ICS_STRIPE_WEBHOOK_SECRET;
      if (!secret) return json({ error: "Stripe billing is not configured" }, 503);
      const body = await request.text();
      if (body.length > MAX_JSON_BODY_BYTES) {
        return json({ error: "Webhook payload is too large" }, 413);
      }
      const verified = await verifyStripe(request, body, secret);
      if (!verified.valid || !verified.event) {
        return json({ error: "Invalid Stripe webhook" }, 401);
      }
      const event = verified.event;
      const eventType = String(event.type ?? "");
      const eventId = String(event.id ?? "");
      const object =
        ((event.data as Record<string, unknown> | undefined)?.object as
          | Record<string, unknown>
          | undefined) ?? {};
      const metadata =
        (object.metadata as Record<string, unknown> | undefined) ?? {};
      const organizationId = String(
        metadata.organization_id ?? object.client_reference_id ?? "",
      );
      const plan = sanitizePlan(metadata.plan);
      const activeEvents = new Set([
        "checkout.session.completed",
        "customer.subscription.created",
        "customer.subscription.updated",
      ]);
      const inactiveEvents = new Set(["customer.subscription.deleted"]);
      if (!activeEvents.has(eventType) && !inactiveEvents.has(eventType)) {
        return json({ status: "ignored" });
      }
      if (!eventId || !organizationId || !plan) {
        return json({ error: "Stripe metadata is incomplete" }, 400);
      }
      const inserted = await env.DB.prepare(
        `INSERT OR IGNORE INTO billing_events (id, event_type, received_at)
         VALUES (?, ?, ?)`,
      )
        .bind(eventId, eventType, nowIso())
        .run();
      if (Number(inserted.meta.changes ?? 0) === 0) {
        return json({ status: "duplicate" });
      }
      const active = activeEvents.has(eventType);
      const updated = await env.DB.prepare(
        `UPDATE organizations
            SET plan = ?, monthly_document_limit = ?, active = ?
          WHERE id = ?`,
      )
        .bind(plan, PLAN_LIMITS[plan], active ? 1 : 0, organizationId)
        .run();
      if (Number(updated.meta.changes ?? 0) === 0) {
        await env.DB.prepare("DELETE FROM billing_events WHERE id = ?")
          .bind(eventId)
          .run();
        return json({ error: "Unknown organization" }, 400);
      }
      return json({ status: "accepted" });
    }

    if (path === "/v1/billing/webhook" && request.method === "POST") {
      const secret = env.ICS_GENERIC_WEBHOOK_SECRET;
      if (!secret) return json({ error: "Billing is not configured" }, 503);
      const body = await request.text();
      if (body.length > MAX_JSON_BODY_BYTES) {
        return json({ error: "Webhook payload is too large" }, 413);
      }
      if (!(await verifyGenericWebhook(request, body, secret))) {
        return json({ error: "Invalid webhook signature" }, 401);
      }
      let payload: Record<string, unknown>;
      try {
        payload = JSON.parse(body) as Record<string, unknown>;
      } catch {
        return json({ error: "Invalid JSON" }, 400);
      }
      const organizationId = String(payload.organization_id ?? "");
      const plan = sanitizePlan(payload.plan);
      const event = String(payload.event ?? "");
      if (!organizationId || !plan || !event) {
        return json({ error: "Billing metadata is incomplete" }, 400);
      }
      const active = event !== "subscription.cancelled";
      await env.DB.prepare(
        `UPDATE organizations
            SET plan = ?, monthly_document_limit = ?, active = ?
          WHERE id = ?`,
      )
        .bind(plan, PLAN_LIMITS[plan], active ? 1 : 0, organizationId)
        .run();
      return json({ status: "accepted" });
    }

    const organization = await authenticate(request, env);
    if (!organization) return json({ error: "Invalid or missing API key" }, 401);

    if (path === "/v1/account" && request.method === "GET") {
      return json({
        id: organization.id,
        name: organization.name,
        plan: organization.plan,
        active: Boolean(organization.active),
        monthly_document_limit: organization.monthly_document_limit,
        documents_used: organization.documents_used,
        remaining_documents: Math.max(
          0,
          organization.monthly_document_limit - organization.documents_used,
        ),
        usage_period: organization.usage_period,
      });
    }

    if (path === "/v1/billing/checkout" && request.method === "POST") {
      const contentLength = Number(request.headers.get("content-length") ?? "0");
      if (contentLength > MAX_JSON_BODY_BYTES) {
        return json({ error: "Billing payload is too large" }, 413);
      }
      let payload: Record<string, unknown>;
      try {
        payload = (await request.json()) as Record<string, unknown>;
      } catch {
        return json({ error: "Invalid JSON" }, 400);
      }
      const plan = payload.plan;
      if (plan !== "starter" && plan !== "pro") {
        return json({ error: "plan must be starter or pro" }, 400);
      }
      const secret = env.STRIPE_SECRET_KEY;
      if (!secret) return json({ error: "Stripe billing is not configured" }, 503);
      const priceId =
        plan === "starter" ? env.STRIPE_PRICE_STARTER : env.STRIPE_PRICE_PRO;
      if (!priceId) return json({ error: "Stripe price is not configured" }, 503);

      const form = new URLSearchParams({
        mode: "subscription",
        "line_items[0][price]": priceId,
        "line_items[0][quantity]": "1",
        success_url: `${env.PUBLIC_BASE_URL}/?checkout=success`,
        cancel_url: `${env.PUBLIC_BASE_URL}/?checkout=cancelled`,
        client_reference_id: organization.id,
        "metadata[organization_id]": organization.id,
        "metadata[plan]": plan,
        "subscription_data[metadata][organization_id]": organization.id,
        "subscription_data[metadata][plan]": plan,
        allow_promotion_codes: "true",
      });
      const response = await fetch("https://api.stripe.com/v1/checkout/sessions", {
        method: "POST",
        headers: {
          authorization: `Bearer ${secret}`,
          "content-type": "application/x-www-form-urlencoded",
        },
        body: form,
      });
      let result: Record<string, unknown>;
      try {
        result = (await response.json()) as Record<string, unknown>;
      } catch {
        return json({ error: "Stripe returned an invalid response" }, 502);
      }
      if (!response.ok) {
        console.error("stripe_checkout_failed", {
          status: response.status,
          error:
            typeof result.error === "object" && result.error
              ? String((result.error as Record<string, unknown>).type ?? "")
              : "",
        });
        return json({ error: "Could not create checkout session" }, 502);
      }
      const checkoutUrl = typeof result.url === "string" ? result.url : "";
      const sessionId = typeof result.id === "string" ? result.id : "";
      if (!checkoutUrl || !sessionId) {
        return json({ error: "Stripe returned an invalid checkout session" }, 502);
      }
      return json({ checkout_url: checkoutUrl, session_id: sessionId }, 201);
    }

    if (path === "/v1/audits" && request.method === "POST") {
      const contentLength = Number(request.headers.get("content-length") ?? "0");
      const maxUpload = Number(env.MAX_UPLOAD_BYTES);
      if (!contentLength) return json({ error: "Content-Length is required" }, 411);
      if (contentLength > maxUpload) return json({ error: "Upload is too large" }, 413);
      if (!request.body) return json({ error: "Upload body is required" }, 400);
      const filename = cleanFilename(request.headers.get("x-ics-filename"));
      if (!filename) {
        return json(
          { error: "X-ICS-Filename must be PDF, DOCX, TXT, or Markdown" },
          400,
        );
      }
      const weights = request.headers.get("x-ics-weights") ?? "default";
      if (
        !["default", "obs-priority", "enf-priority", "rev-priority", "esg-balanced"].includes(
          weights,
        )
      ) {
        return json({ error: "Unknown weight preset" }, 400);
      }
      const contentType =
        request.headers.get("content-type") ?? "application/octet-stream";
      const jobId = `job_${crypto.randomUUID().replaceAll("-", "")}`;
      const uploadKey = `orgs/${organization.id}/uploads/${jobId}/${filename}`;
      const reserved = await reserveJob(
        env,
        organization.id,
        jobId,
        filename,
        contentType,
        contentLength,
        uploadKey,
        weights,
      );
      if (!reserved) return json({ error: "Monthly document quota exhausted" }, 429);
      try {
        await env.REPORTS.put(uploadKey, request.body, {
          httpMetadata: { contentType },
          customMetadata: {
            organization_id: organization.id,
            job_id: jobId,
          },
        });
        await env.AUDIT_QUEUE.send({ job_id: jobId });
      } catch (error) {
        await refundReservation(
          env,
          jobId,
          error instanceof Error ? error.message : String(error),
        );
        await env.REPORTS.delete(uploadKey);
        return json({ error: "Could not queue audit" }, 500);
      }
      const job = await env.DB.prepare("SELECT * FROM audit_jobs WHERE id = ?")
        .bind(jobId)
        .first<AuditJob>();
      if (!job) return json({ error: "Could not create audit job" }, 500);
      return json(
        {
          ...jobPayload(job),
          poll_url: `/v1/audits/${jobId}`,
          report_url: `/v1/audits/${jobId}/report`,
        },
        202,
      );
    }

    const jobMatch = /^\/v1\/audits\/([^/]+)(\/report)?$/.exec(path);
    if (jobMatch) {
      const [, jobId, reportSuffix] = jobMatch;
      const job = await env.DB.prepare(
        "SELECT * FROM audit_jobs WHERE id = ? AND organization_id = ?",
      )
        .bind(jobId, organization.id)
        .first<AuditJob>();
      if (!job) return json({ error: "Audit job not found" }, 404);
      if (request.method === "GET" && !reportSuffix) return json(jobPayload(job));
      if (request.method === "GET" && reportSuffix) {
        if (job.status !== "completed") {
          return json({ error: "Audit report is not ready" }, 409);
        }
        if (!job.report_key) return json({ error: "Audit report has expired" }, 410);
        const object = await env.REPORTS.get(job.report_key);
        if (!object?.body) return json({ error: "Audit report has expired" }, 410);
        return new Response(object.body, {
          headers: {
            "content-type": "application/json; charset=utf-8",
            "content-disposition": `inline; filename="${jobId}.json"`,
            "cache-control": "no-store",
            "x-content-type-options": "nosniff",
          },
        });
      }
      if (request.method === "DELETE") {
        await env.DB.prepare(
          `UPDATE audit_jobs
              SET status = 'cancelled', completed_at = ?
            WHERE id = ? AND organization_id = ?
              AND status IN ('queued', 'running', 'failed', 'completed')`,
        )
          .bind(nowIso(), jobId, organization.id)
          .run();
        const keys = [job.upload_key, job.report_key].filter(
          (key): key is string => Boolean(key),
        );
        if (keys.length) await env.REPORTS.delete(keys);
        try {
          await env.AUDIT_CONTAINER.getByName(jobId).stopContainer();
        } catch (error) {
          console.error("audit_container_stop_failed", {
            job_id: jobId,
            error: error instanceof Error ? error.message : String(error),
          });
        }
        return new Response(null, { status: 204, headers: jsonHeaders });
      }
    }

    return json({ error: "Not found" }, 404);
  },

  async queue(
    batch: MessageBatch<QueueJob>,
    env: Env,
  ): Promise<void> {
    for (const message of batch.messages) {
      try {
        await processQueueMessage(message, env);
      } catch (error) {
        console.error("queue_job_failed", {
          job_id: message.body.job_id,
          error: error instanceof Error ? error.message : String(error),
        });
        message.retry({ delaySeconds: Math.min(120, 30 * message.attempts) });
      }
    }
  },

  async scheduled(
    _controller: ScheduledController,
    env: Env,
  ): Promise<void> {
    const retentionDays = Number(env.REPORT_RETENTION_DAYS);
    const cutoff = new Date(
      Date.now() - retentionDays * 24 * 60 * 60 * 1000,
    ).toISOString();
    const expired = await env.DB.prepare(
      `SELECT id, report_key FROM audit_jobs
        WHERE status = 'completed' AND completed_at < ?
          AND report_key IS NOT NULL
        LIMIT 200`,
    )
      .bind(cutoff)
      .all<{ id: string; report_key: string }>();
    const keys = expired.results.map((row) => row.report_key);
    if (keys.length) {
      await env.REPORTS.delete(keys);
      await env.DB.batch(
        expired.results.map((row) =>
          env.DB.prepare("UPDATE audit_jobs SET report_key = NULL WHERE id = ?").bind(
            row.id,
          ),
        ),
      );
    }
    const abandoned = await env.DB.prepare(
      `SELECT id, upload_key FROM audit_jobs
        WHERE status IN ('failed', 'cancelled') AND completed_at < ?
        LIMIT 200`,
    )
      .bind(cutoff)
      .all<{ id: string; upload_key: string }>();
    const abandonedKeys = abandoned.results.map((row) => row.upload_key);
    if (abandonedKeys.length) await env.REPORTS.delete(abandonedKeys);

    const metadataRetentionDays = Number(env.JOB_METADATA_RETENTION_DAYS);
    const metadataCutoff = new Date(
      Date.now() - metadataRetentionDays * 24 * 60 * 60 * 1000,
    ).toISOString();
    await env.DB.prepare(
      `DELETE FROM audit_jobs
        WHERE id IN (
          SELECT id FROM audit_jobs
           WHERE status IN ('completed', 'failed', 'cancelled')
             AND created_at < ?
           LIMIT 200
        )`,
    )
      .bind(metadataCutoff)
      .run();
  },
} satisfies ExportedHandler<Env, QueueJob>;
