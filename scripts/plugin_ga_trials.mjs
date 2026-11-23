import { spawn } from "node:child_process";
import { readFile } from "node:fs/promises";
import path from "node:path";
import readline from "node:readline";

const root = path.resolve(import.meta.dirname, "..");
const testHome = path.join(root, ".plugin-local-test-home");
const cacheRoot = path.join(testHome, "plugins", "cache", "ics-tec");
const credentialsRoot = path.join(root, ".esg-commitment-audit-service");
const evidencePackPath = path.join(root, "audit-output", "evidence-pack.zip");
const aiPolicy = `# Responsible AI Policy

## Scope and authority
This policy applies to all production AI systems. The AI Governance Board is
the accountable owner and approves amendments after public consultation.

## Revision and version control
The policy is reviewed every six months and after material incidents. Every
change has a semantic version, dated changelog, retained prior version, and
published diff. Any affected person may propose a revision through the
governance portal.

## Gradual deployment and rollback
Changes move through sandbox, limited deployment, and general deployment.
The Board or Safety Lead may pause or roll back immediately. Rollback authority,
conditions, protected safety clauses, and the rollback procedure are documented.
Rollback exercises occur quarterly.

## Notice, explanation, appeal, refusal and exit
Affected people receive 30 days notice where feasible. A human reviewer provides
written explanations and handles appeals within ten business days. Users may
refuse automated processing, withdraw consent, and request a non-AI alternative.

## Monitoring, audit and retention
The system logs decisions, model versions, overrides, and incidents for at least
three years. Monitoring metrics and audit records are reviewed monthly.

## Independent oversight and uncertainty
An independent external panel reviews high-risk changes. A confidential escalation
channel protects whistleblowers. Uncertainty and dissenting opinions are recorded.

## Capability gates and interruption
Capability thresholds, evaluation gates, named stop authority, rollback drills,
interruption procedures, and public incident reporting are documented.
`;

class McpClient {
  constructor({ product, serverPath, apiKey }) {
    this.nextId = 1;
    this.pending = new Map();
    this.process = spawn(process.execPath, [serverPath], {
      cwd: path.dirname(serverPath),
      env: {
        ...process.env,
        ICS_PRODUCT: product,
        ICS_AUDIT_API_KEY: apiKey,
        NODE_NO_WARNINGS: "1",
      },
      stdio: ["pipe", "pipe", "pipe"],
    });
    this.stderr = "";
    this.process.stderr.on("data", (chunk) => {
      this.stderr += chunk.toString();
    });
    const lines = readline.createInterface({
      input: this.process.stdout,
      crlfDelay: Infinity,
    });
    lines.on("line", (line) => {
      const message = JSON.parse(line);
      const pending = this.pending.get(message.id);
      if (!pending) return;
      this.pending.delete(message.id);
      if (message.error) pending.reject(new Error(message.error.message));
      else pending.resolve(message.result);
    });
  }

  request(method, params = {}) {
    const id = this.nextId++;
    this.process.stdin.write(`${JSON.stringify({ jsonrpc: "2.0", id, method, params })}\n`);
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
    });
  }

  async initialize() {
    return this.request("initialize", {
      protocolVersion: "2025-06-18",
      clientInfo: { name: "ics-ga-trial", version: "1.0.0" },
    });
  }

  async call(name, args = {}) {
    return this.request("tools/call", { name, arguments: args });
  }

  close() {
    this.process.stdin.end();
    this.process.kill();
  }
}

async function credential(fileName) {
  const record = JSON.parse(
    await readFile(path.join(credentialsRoot, fileName), "utf8"),
  );
  if (!record.api_key) throw new Error(`Missing API key in ${fileName}`);
  return record.api_key;
}

async function waitForReport(client, jobId, maxAttempts = 45) {
  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    const response = await client.call("get_cloud_audit", {
      job_id: jobId,
      include_report: true,
    });
    if (response.isError) {
      throw new Error(response.content?.[0]?.text || "Cloud status failed");
    }
    const status = response.structuredContent;
    if (status.status === "completed") return status.report;
    if (status.status === "failed") {
      throw new Error(`Job ${jobId} failed: ${status.error || "unknown error"}`);
    }
    await new Promise((resolve) => setTimeout(resolve, 2000));
  }
  throw new Error(`Timed out waiting for ${jobId}`);
}

function reportMetric(report) {
  if (Array.isArray(report.commitments)) {
    return { metric: "commitments", count: report.commitments.length };
  }
  return {
    metric: "checks",
    count: (report.dimensions || []).reduce(
      (total, dimension) => total + (dimension.checks?.length || 0),
      0,
    ),
  };
}

async function runAuditPersona({
  persona,
  product,
  serverPath,
  apiKey,
  text,
  profile,
  expectedChecks,
}) {
  const client = new McpClient({ product, serverPath, apiKey });
  try {
    await client.initialize();
    const account = await client.call("get_account");
    if (account.isError || account.structuredContent.compatible !== true) {
      throw new Error(`${persona}: account is not compatible`);
    }
    const created = await client.call("audit_text", {
      text,
      filename: `${persona.toLowerCase().replaceAll(" ", "-")}.md`,
      ...(profile ? { profile } : {}),
    });
    if (created.isError) {
      throw new Error(created.content?.[0]?.text || `${persona}: upload failed`);
    }
    const job = created.structuredContent;
    const report = await waitForReport(client, job.id);
    const metric = reportMetric(report);
    if (
      metric.metric === "checks" &&
      expectedChecks &&
      metric.count !== expectedChecks
    ) {
      throw new Error(
        `${persona}: expected ${expectedChecks} checks, got ${metric.count}`,
      );
    }
    await client.call("delete_cloud_audit", { job_id: job.id });
    return {
      persona,
      result: "passed",
      plan: account.structuredContent.plan,
      report_type: report.report_type,
      metric: metric.metric,
      count: metric.count,
      job_id: job.id,
    };
  } finally {
    client.close();
  }
}

const esgServer = path.join(
  cacheRoot,
  "esg-commitment-audit",
  "0.6.0",
  "server.mjs",
);
const aiServer = path.join(
  cacheRoot,
  "ai-alignment-revisability-audit",
  "0.6.0",
  "server.mjs",
);
const esgKey = await credential("plugin-esg-0.6.0-smoke.json");
const aiKey = await credential("plugin-ai-0.6.0-smoke.json");

const results = [];
results.push(
  await runAuditPersona({
    persona: "ESG sustainability analyst",
    product: "esg",
    serverPath: esgServer,
    apiKey: esgKey,
    text: `Our climate target is to reduce absolute Scope 1 and Scope 2 emissions
by 50% from a 2024 baseline by 2030. The Chief Sustainability Officer owns
delivery. Progress is measured annually using the GHG Protocol, verified by an
independent assurance provider, and reported in the annual sustainability
report. Material revision triggers, remedy procedures and exit terms are
documented.`,
    expectedChecks: 0,
  }),
);

results.push(
  await runAuditPersona({
    persona: "AI policy lead",
    product: "ai",
    serverPath: aiServer,
    apiKey: aiKey,
    text: aiPolicy,
    profile: "general",
    expectedChecks: 28,
  }),
);

results.push(
  await runAuditPersona({
    persona: "Insurance governance reviewer",
    product: "ai",
    serverPath: aiServer,
    apiKey: aiKey,
    text: `${aiPolicy}

## Insurance safeguards
Adverse automated decisions include a plain-language explanation, an accessible
appeal route, and independent human review before the decision becomes final.`,
    profile: "insurance",
    expectedChecks: 30,
  }),
);

{
  const client = new McpClient({
    product: "ai",
    serverPath: aiServer,
    apiKey: aiKey,
  });
  try {
    await client.initialize();
    const created = await client.call("audit_evidence_pack", {
      path: evidencePackPath,
    });
    if (created.isError) {
      throw new Error(
        created.content?.[0]?.text || "Evidence-pack upload failed",
      );
    }
    const job = created.structuredContent;
    const report = await waitForReport(client, job.id);
    await client.call("delete_cloud_audit", { job_id: job.id });
    results.push({
      persona: "AI evidence manager",
      result: "passed",
      plan: "ai-founding-team",
      report_type: report.report_type,
      artifacts: report.artifact_inventory.length,
      promotions: report.promotions.length,
      job_id: job.id,
    });
  } finally {
    client.close();
  }
}

{
  const client = new McpClient({
    product: "ai",
    serverPath: aiServer,
    apiKey: esgKey,
  });
  try {
    await client.initialize();
    const response = await client.call("audit_text", {
      text: "This request must stop before upload.",
      filename: "wrong-key.md",
      profile: "general",
    });
    if (!response.isError) {
      throw new Error("Wrong-product key unexpectedly created an AI job");
    }
    const message = response.content?.[0]?.text || "";
    if (!message.includes("cannot run 'ai-revisability'")) {
      throw new Error(`Wrong-product error was not actionable: ${message}`);
    }
    results.push({
      persona: "Misconfigured ESG key user",
      result: "passed",
      guard: "rejected before upload",
    });
  } finally {
    client.close();
  }
}

console.log(JSON.stringify({ trials: results }, null, 2));
