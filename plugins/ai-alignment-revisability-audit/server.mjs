import { open, readFile, stat } from "node:fs/promises";
import path from "node:path";
import readline from "node:readline";
import { pathToFileURL } from "node:url";

const SERVER_VERSION = "0.5.0";
const PROTOCOL_VERSION = "2025-06-18";
const MAX_DOCUMENT_BYTES = 50 * 1024 * 1024;
const MAX_EVIDENCE_PACK_BYTES = 100 * 1024 * 1024;
const REVIEW_PROFILES = [
  "general",
  "news_media",
  "advertising",
  "insurance",
  "industrial_design",
];

const documentContentTypes = {
  ".pdf": "application/pdf",
  ".docx":
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ".txt": "text/plain; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
  ".markdown": "text/markdown; charset=utf-8",
};

const PRODUCTS = {
  esg: {
    id: "esg",
    serverName: "esg-commitment-audit",
    displayName: "ESG Commitment Audit",
    modes: ["commitment", "recursive-freedom"],
    defaultMode: "commitment",
    requiredCloudModes: ["commitment"],
    activationUrl:
      "https://esg-commitment-audit-api.franka328162810.workers.dev/activate",
    gumroadUrl: "https://icsstudies.gumroad.com/l/esg-commitment-audit",
    keyInstruction:
      "Subscribe on Gumroad, activate the license at the ESG activation page, and set ICS_AUDIT_API_KEY.",
  },
  ai: {
    id: "ai",
    serverName: "ai-alignment-revisability-audit",
    displayName: "AI Alignment Revisability Audit",
    modes: ["ai-revisability"],
    defaultMode: "ai-revisability",
    requiredCloudModes: ["ai-revisability"],
    activationUrl:
      "https://esg-commitment-audit-api.franka328162810.workers.dev/ai-revisability-audit/activate",
    gumroadUrl:
      "https://icsstudies.gumroad.com/l/ai-alignment-revisability-audit",
    keyInstruction:
      "Subscribe on Gumroad, activate the license at the AI activation page, and set ICS_AUDIT_API_KEY.",
  },
};

function currentProduct() {
  const product = PRODUCTS[String(process.env.ICS_PRODUCT || "").toLowerCase()];
  if (!product) {
    throw new Error("ICS_PRODUCT must be configured as 'esg' or 'ai'");
  }
  return product;
}

function toolDefinitions(product) {
  const auditProperties = {
    path: {
      type: "string",
      description: "Absolute local path to the document",
    },
    ...(product.id === "esg"
      ? {
          weights: {
            type: "string",
            enum: [
              "default",
              "obs-priority",
              "enf-priority",
              "rev-priority",
              "esg-balanced",
            ],
            default: "default",
          },
          mode: {
            type: "string",
            enum: product.modes,
            default: product.defaultMode,
          },
        }
      : {
          profile: {
            type: "string",
            enum: REVIEW_PROFILES,
            default: "general",
          },
        }),
  };
  const textProperties = {
    text: { type: "string" },
    filename: {
      type: "string",
      default: product.id === "ai" ? "ai-policy.txt" : "pasted-text.txt",
    },
    ...(product.id === "esg"
      ? {
          weights: { type: "string", default: "default" },
          mode: {
            type: "string",
            enum: product.modes,
            default: product.defaultMode,
          },
        }
      : {
          profile: {
            type: "string",
            enum: REVIEW_PROFILES,
            default: "general",
          },
        }),
  };
  const tools = [
    {
      name: "audit_document",
      description:
        product.id === "ai"
          ? "Upload a PDF, DOCX, TXT, or Markdown AI policy to the authorized ICS hosted API and create a revisability audit job."
          : "Upload a PDF, DOCX, TXT, or Markdown ESG report to the authorized ICS hosted API and create a commitment audit job.",
      inputSchema: {
        type: "object",
        properties: auditProperties,
        required: ["path"],
        additionalProperties: false,
      },
      annotations: { destructiveHint: false },
    },
    {
      name: "audit_text",
      description:
        product.id === "ai"
          ? "Upload pasted AI governance text and create a revisability audit job."
          : "Upload pasted ESG commitment text and create a commitment audit job.",
      inputSchema: {
        type: "object",
        properties: textProperties,
        required: ["text"],
        additionalProperties: false,
      },
      annotations: { destructiveHint: false },
    },
  ];
  if (product.id === "ai") {
    tools.push({
      name: "audit_evidence_pack",
      description:
        "Upload a sealed evidence-pack ZIP, verify SHA-256 pins, and propose human-confirmed E2/E3/E4 grade upgrades.",
      inputSchema: {
        type: "object",
        properties: {
          path: {
            type: "string",
            description: "Absolute local path to an evidence-pack ZIP",
          },
        },
        required: ["path"],
        additionalProperties: false,
      },
      annotations: { destructiveHint: false },
    });
  }
  tools.push(
    {
      name: "get_cloud_audit",
      description:
        "Get an audit job status and optionally fetch its completed JSON report.",
      inputSchema: {
        type: "object",
        properties: {
          job_id: { type: "string" },
          include_report: { type: "boolean", default: false },
        },
        required: ["job_id"],
        additionalProperties: false,
      },
      annotations: { readOnlyHint: true },
    },
    {
      name: "get_account",
      description:
        "Show the current plan, usage, monthly limit, allowed modes, and compatibility with this plugin.",
      inputSchema: {
        type: "object",
        properties: {},
        additionalProperties: false,
      },
      annotations: { readOnlyHint: true },
    },
    {
      name: "delete_cloud_audit",
      description:
        "Delete the source and report for an audit owned by the current API key.",
      inputSchema: {
        type: "object",
        properties: {
          job_id: { type: "string" },
        },
        required: ["job_id"],
        additionalProperties: false,
      },
      annotations: { destructiveHint: true },
    },
  );
  return tools;
}

function cloudConfig() {
  const product = currentProduct();
  const baseUrl = (
    process.env.ICS_AUDIT_API_URL ||
    process.env.ESG_AUDIT_API_URL ||
    "https://esg-commitment-audit-api.franka328162810.workers.dev"
  ).replace(/\/+$/, "");
  const apiKey =
    process.env.ICS_AUDIT_API_KEY || process.env.ESG_AUDIT_API_KEY || "";
  if (!apiKey) {
    throw new Error(
      `${product.displayName} requires an API key. ${product.keyInstruction} ` +
        `Activation: ${product.activationUrl}`,
    );
  }
  if (
    !baseUrl.startsWith("https://") &&
    !baseUrl.startsWith("http://127.0.0.1")
  ) {
    throw new Error("ICS_AUDIT_API_URL must use HTTPS or loopback HTTP");
  }
  return { baseUrl, apiKey, product };
}

function recoveryMessage(status, payload, product) {
  if (status === 401) {
    return "The API key is missing, invalid, or revoked. Issue a new key through the activation page.";
  }
  if (status === 403) {
    return (
      `This API key cannot use ${product.displayName}. Check that the matching plan ` +
      `is active and that the license was not cancelled or refunded. Activation: ${product.activationUrl}`
    );
  }
  if (status === 409) {
    return "The request conflicts with the current account or job state. Query the account or job before retrying.";
  }
  if (status === 413) {
    return product.id === "ai"
      ? "The upload is too large. Documents are limited to 50 MB; evidence-pack ZIPs are limited to 100 MB compressed and 200 MB uncompressed."
      : "The upload is too large. Documents are limited to 50 MB and 100 pages.";
  }
  if (status === 415) {
    return "The upload type is unsupported or the PDF has no text layer.";
  }
  if (status === 429) {
    return "The monthly allowance is exhausted. Wait for the next usage period or upgrade the plan.";
  }
  if (status === 503) {
    return "The hosted service is temporarily unavailable. Do not repeat an upload automatically because the first request may already have created a job.";
  }
  const detail = payload?.error ? ` ${payload.error}` : "";
  return `The hosted API returned HTTP ${status}.${detail}`;
}

async function cloudRequest(
  method,
  requestPath,
  { body = undefined, contentType = undefined, headers = {} } = {},
) {
  const { baseUrl, apiKey, product } = cloudConfig();
  const attempts = method === "GET" ? 3 : 1;
  let lastError;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      const response = await fetch(`${baseUrl}${requestPath}`, {
        method,
        body,
        headers: {
          Authorization: `Bearer ${apiKey}`,
          Accept: "application/json",
          "User-Agent": `${product.serverName}-plugin/${SERVER_VERSION}`,
          ...(contentType ? { "Content-Type": contentType } : {}),
          ...headers,
        },
        signal: AbortSignal.timeout(240_000),
      });
      const text = await response.text();
      let payload = {};
      try {
        payload = text ? JSON.parse(text) : {};
      } catch {
        payload = { raw: text.slice(0, 500) };
      }
      if (!response.ok) {
        throw new Error(recoveryMessage(response.status, payload, product));
      }
      return payload;
    } catch (error) {
      lastError = error;
      const retryableGet =
        method === "GET" &&
        attempt < attempts &&
        !/HTTP (400|401|403|404|409|413|415|429)/.test(
          String(error?.message || ""),
        );
      if (!retryableGet) break;
      await new Promise((resolve) => setTimeout(resolve, 500 * attempt));
    }
  }
  if (method !== "GET") {
    throw new Error(
      `Upload outcome is uncertain: ${lastError?.message || String(lastError)} ` +
        "The plugin does not retry uploads automatically. Call get_account and inspect recent activity before retrying.",
    );
  }
  throw lastError;
}

function accountCompatibility(account, product) {
  const allowed = Array.isArray(account.allowed_audit_modes)
    ? account.allowed_audit_modes
    : [];
  return {
    plugin_product: product.id,
    compatible: product.requiredCloudModes.some((mode) =>
      allowed.includes(mode),
    ),
    expected_modes: product.requiredCloudModes,
    activation_url: product.activationUrl,
  };
}

async function getAccount(product) {
  const account = await cloudRequest("GET", "/v1/account");
  return { ...account, ...accountCompatibility(account, product) };
}

async function ensureProductAccess(product, requiredMode) {
  const account = await getAccount(product);
  const allowed = Array.isArray(account.allowed_audit_modes)
    ? account.allowed_audit_modes
    : [];
  if (!allowed.includes(requiredMode)) {
    throw new Error(
      `${product.displayName} cannot run '${requiredMode}' with this API key. ` +
        `Current plan: ${account.plan || "unknown"}; allowed modes: ${
          allowed.join(", ") || "none"
        }. ${product.keyInstruction} Activation: ${product.activationUrl}`,
    );
  }
  return account;
}

function cleanMode(product, requested) {
  const mode = String(requested || product.defaultMode);
  if (!product.modes.includes(mode)) {
    throw new Error(
      `${product.displayName} supports these modes: ${product.modes.join(", ")}`,
    );
  }
  return mode;
}

async function submitDocument(args, product) {
  const resolved = path.resolve(String(args.path || ""));
  const extension = path.extname(resolved).toLowerCase();
  const contentType = documentContentTypes[extension];
  if (!contentType) {
    throw new Error(
      `Unsupported file type '${extension || "(none)"}'. Use PDF, DOCX, TXT, or Markdown.`,
    );
  }
  const info = await stat(resolved);
  if (!info.isFile()) throw new Error(`Not a file: ${resolved}`);
  if (info.size === 0) throw new Error("The selected file is empty");
  if (info.size > MAX_DOCUMENT_BYTES) {
    throw new Error("The selected file exceeds the 50 MB document limit");
  }
  const mode =
    product.id === "ai" ? product.defaultMode : cleanMode(product, args.mode);
  const account = await ensureProductAccess(product, mode);
  const body = await readFile(resolved);
  const result = await cloudRequest("POST", "/v1/audits", {
    body,
    contentType,
    headers: {
      "X-ESG-Filename": encodeURIComponent(path.basename(resolved)),
      "X-ESG-Weights": String(args.weights || "default"),
      "X-ESG-Mode": mode,
      "X-ESG-Profile": String(args.profile || "general"),
    },
  });
  return { ...result, plugin_product: product.id, account_plan: account.plan };
}

async function submitText(args, product) {
  const text = String(args.text || "");
  if (!text || text.length > 2_000_000) {
    throw new Error("Text must contain between 1 and 2,000,000 characters");
  }
  const requestedName = String(
    args.filename || (product.id === "ai" ? "ai-policy.txt" : "pasted-text.txt"),
  );
  const filename = /\.[a-z0-9]+$/i.test(requestedName)
    ? requestedName
    : `${requestedName}.txt`;
  const extension = path.extname(filename).toLowerCase();
  if (!documentContentTypes[extension]) {
    throw new Error("Pasted text filename must use TXT or Markdown");
  }
  const mode =
    product.id === "ai" ? product.defaultMode : cleanMode(product, args.mode);
  const account = await ensureProductAccess(product, mode);
  const result = await cloudRequest("POST", "/v1/audits", {
    body: Buffer.from(text, "utf8"),
    contentType: documentContentTypes[extension],
    headers: {
      "X-ESG-Filename": encodeURIComponent(filename),
      "X-ESG-Weights": String(args.weights || "default"),
      "X-ESG-Mode": mode,
      "X-ESG-Profile": String(args.profile || "general"),
    },
  });
  return { ...result, plugin_product: product.id, account_plan: account.plan };
}

async function submitEvidencePack(args, product) {
  if (product.id !== "ai") {
    throw new Error("Evidence-pack review is available only in the AI plugin");
  }
  const resolved = path.resolve(String(args.path || ""));
  if (path.extname(resolved).toLowerCase() !== ".zip") {
    throw new Error("Evidence-pack review requires a ZIP archive");
  }
  const info = await stat(resolved);
  if (!info.isFile()) throw new Error(`Not a file: ${resolved}`);
  if (info.size === 0) throw new Error("The evidence-pack ZIP is empty");
  if (info.size > MAX_EVIDENCE_PACK_BYTES) {
    throw new Error("The evidence-pack ZIP exceeds the 100 MB compressed limit");
  }
  const handle = await open(resolved, "r");
  const signature = Buffer.alloc(4);
  try {
    await handle.read(signature, 0, 4, 0);
  } finally {
    await handle.close();
  }
  const isZip =
    signature.equals(Buffer.from([0x50, 0x4b, 0x03, 0x04])) ||
    signature.equals(Buffer.from([0x50, 0x4b, 0x05, 0x06]));
  if (!isZip) throw new Error("The selected file is not a valid ZIP archive");
  const account = await ensureProductAccess(product, "evidence-pack");
  const body = await readFile(resolved);
  const result = await cloudRequest("POST", "/v1/audits", {
    body,
    contentType: "application/zip",
    headers: {
      "X-ESG-Filename": encodeURIComponent(path.basename(resolved)),
      "X-ESG-Mode": "evidence-pack",
    },
  });
  return { ...result, plugin_product: product.id, account_plan: account.plan };
}

export async function callTool(name, args = {}) {
  const product = currentProduct();
  if (name === "audit_document") return submitDocument(args, product);
  if (name === "audit_text") return submitText(args, product);
  if (name === "audit_evidence_pack") return submitEvidencePack(args, product);
  if (name === "get_account") return getAccount(product);
  if (name === "get_cloud_audit") {
    const jobId = String(args.job_id || "");
    if (!jobId) throw new Error("job_id is required");
    const status = await cloudRequest(
      "GET",
      `/v1/audits/${encodeURIComponent(jobId)}`,
    );
    if (args.include_report && status.status === "completed") {
      status.report = await cloudRequest(
        "GET",
        `/v1/audits/${encodeURIComponent(jobId)}/report`,
      );
    }
    return status;
  }
  if (name === "delete_cloud_audit") {
    const jobId = String(args.job_id || "");
    if (!jobId) throw new Error("job_id is required");
    await cloudRequest("DELETE", `/v1/audits/${encodeURIComponent(jobId)}`);
    return { deleted: true, job_id: jobId };
  }
  throw new Error(`Unknown tool: ${name}`);
}

function toolResult(value) {
  return {
    content: [{ type: "text", text: JSON.stringify(value) }],
    structuredContent: value,
    isError: false,
  };
}

function toolError(error) {
  return {
    content: [
      {
        type: "text",
        text: `${error?.name || "Error"}: ${error?.message || String(error)}`,
      },
    ],
    isError: true,
  };
}

function response(id, result) {
  return { jsonrpc: "2.0", id, result };
}

export async function handleMessage(message) {
  const method = message?.method;
  const id = message?.id;
  if (method === "initialize") {
    const product = currentProduct();
    return response(id, {
      protocolVersion: PROTOCOL_VERSION,
      capabilities: { tools: {} },
      serverInfo: { name: product.serverName, version: SERVER_VERSION },
    });
  }
  if (
    method === "notifications/initialized" ||
    method === "notifications/cancelled"
  ) {
    return null;
  }
  if (method === "ping") return response(id, {});
  if (method === "tools/list") {
    return response(id, { tools: toolDefinitions(currentProduct()) });
  }
  if (method === "tools/call") {
    const params = message.params || {};
    try {
      const value = await callTool(
        String(params.name || ""),
        params.arguments || {},
      );
      return response(id, toolResult(value));
    } catch (error) {
      return response(id, toolError(error));
    }
  }
  if (id === undefined || id === null) return null;
  return {
    jsonrpc: "2.0",
    id,
    error: { code: -32601, message: `Method not found: ${method}` },
  };
}

async function main() {
  const input = readline.createInterface({
    input: process.stdin,
    crlfDelay: Infinity,
  });
  for await (const line of input) {
    if (!line.trim()) continue;
    let result;
    try {
      result = await handleMessage(JSON.parse(line));
    } catch (error) {
      result = {
        jsonrpc: "2.0",
        id: null,
        error: { code: -32700, message: `Parse error: ${error.message}` },
      };
    }
    if (result) process.stdout.write(`${JSON.stringify(result)}\n`);
  }
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href
) {
  await main();
}
