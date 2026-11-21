import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import readline from "node:readline";
import { pathToFileURL } from "node:url";

const SERVER_NAME = "ics-commitment-audit";
const SERVER_VERSION = "0.2.0";
const PROTOCOL_VERSION = "2025-06-18";
const MAX_UPLOAD_BYTES = 50 * 1024 * 1024;

const contentTypes = {
  ".pdf": "application/pdf",
  ".docx":
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ".txt": "text/plain; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
  ".markdown": "text/markdown; charset=utf-8",
};

const tools = [
  {
    name: "audit_document",
    description:
      "Upload a PDF, DOCX, TXT, or Markdown report to the authorized ICS hosted API and create an audit job.",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "Absolute local path to the report",
        },
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
      },
      required: ["path"],
      additionalProperties: false,
    },
    annotations: { destructiveHint: false },
  },
  {
    name: "audit_text",
    description:
      "Upload pasted text to the authorized ICS hosted API and create an audit job.",
    inputSchema: {
      type: "object",
      properties: {
        text: { type: "string" },
        filename: { type: "string", default: "pasted-text.txt" },
        weights: { type: "string", default: "default" },
      },
      required: ["text"],
      additionalProperties: false,
    },
    annotations: { destructiveHint: false },
  },
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
      "Show the current plan, monthly limit, usage, and remaining audit allowance.",
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
];

function cloudConfig() {
  const baseUrl = (
    process.env.ICS_AUDIT_API_URL ||
    "https://ics-commitment-audit-api.franka328162810.workers.dev"
  ).replace(/\/+$/, "");
  const apiKey = process.env.ICS_AUDIT_API_KEY || "";
  if (!apiKey) {
    throw new Error(
      "ICS_AUDIT_API_KEY is required. Configure the plugin environment with a trial or paid API key.",
    );
  }
  if (!baseUrl.startsWith("https://") && !baseUrl.startsWith("http://127.0.0.1")) {
    throw new Error("ICS_AUDIT_API_URL must use HTTPS or loopback HTTP");
  }
  return { baseUrl, apiKey };
}

async function cloudRequest(
  method,
  requestPath,
  { body = undefined, contentType = undefined, headers = {} } = {},
) {
  const { baseUrl, apiKey } = cloudConfig();
  const response = await fetch(`${baseUrl}${requestPath}`, {
    method,
    body,
    headers: {
      Authorization: `Bearer ${apiKey}`,
      Accept: "application/json",
      "User-Agent": `ics-commitment-audit-plugin/${SERVER_VERSION}`,
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
    throw new Error(
      `Cloud API returned HTTP ${response.status}: ${JSON.stringify(payload)}`,
    );
  }
  return payload;
}

async function submitDocument(filePath, weights) {
  const resolved = path.resolve(filePath);
  const extension = path.extname(resolved).toLowerCase();
  const contentType = contentTypes[extension];
  if (!contentType) {
    throw new Error(
      `Unsupported file type '${extension || "(none)"}'. Use PDF, DOCX, TXT, or Markdown.`,
    );
  }
  const info = await stat(resolved);
  if (!info.isFile()) throw new Error(`Not a file: ${resolved}`);
  if (info.size === 0) throw new Error("The selected file is empty");
  if (info.size > MAX_UPLOAD_BYTES) {
    throw new Error("The selected file exceeds the 50 MB upload limit");
  }
  const body = await readFile(resolved);
  return cloudRequest("POST", "/v1/audits", {
    body,
    contentType,
    headers: {
      "X-ICS-Filename": encodeURIComponent(path.basename(resolved)),
      "X-ICS-Weights": String(weights || "default"),
    },
  });
}

async function submitText(text, filename, weights) {
  if (!text || text.length > 2_000_000) {
    throw new Error("Text must contain between 1 and 2,000,000 characters");
  }
  const safeName = String(filename || "pasted-text.txt");
  const finalName = /\.[a-z0-9]+$/i.test(safeName) ? safeName : `${safeName}.txt`;
  return cloudRequest("POST", "/v1/audits", {
    body: Buffer.from(text, "utf8"),
    contentType: contentTypes[path.extname(finalName).toLowerCase()] || "text/plain",
    headers: {
      "X-ICS-Filename": encodeURIComponent(finalName),
      "X-ICS-Weights": String(weights || "default"),
    },
  });
}

async function callTool(name, args) {
  if (name === "audit_document") {
    return submitDocument(String(args.path), args.weights);
  }
  if (name === "audit_text") {
    return submitText(
      String(args.text),
      String(args.filename || "pasted-text.txt"),
      args.weights,
    );
  }
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
  if (name === "get_account") {
    return cloudRequest("GET", "/v1/account");
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
    return response(id, {
      protocolVersion: PROTOCOL_VERSION,
      capabilities: { tools: {} },
      serverInfo: { name: SERVER_NAME, version: SERVER_VERSION },
    });
  }
  if (
    method === "notifications/initialized" ||
    method === "notifications/cancelled"
  ) {
    return null;
  }
  if (method === "ping") return response(id, {});
  if (method === "tools/list") return response(id, { tools });
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
