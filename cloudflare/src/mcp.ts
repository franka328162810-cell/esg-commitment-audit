type McpProduct = "esg" | "ai";

const PROTOCOL_VERSION = "2025-06-18";
const REMOTE_VERSION = "0.6.2";
const MAX_DOCUMENT_BYTES = 50 * 1024 * 1024;
const MAX_REMOTE_EVIDENCE_BYTES = 70 * 1024 * 1024;
const PROFILE_VALUES = [
  "general",
  "news_media",
  "advertising",
  "insurance",
  "industrial_design",
] as const;

interface ProductDefinition {
  id: McpProduct;
  serverName: string;
  displayName: string;
  activationUrl: string;
  defaultMode: string;
  modes: string[];
  requiredMode: string;
}

const PRODUCTS: Record<McpProduct, ProductDefinition> = {
  esg: {
    id: "esg",
    serverName: "esg-commitment-audit-remote",
    displayName: "ESG Commitment Audit",
    activationUrl: "https://esg-commitment-audit-api.franka328162810.workers.dev/activate",
    defaultMode: "commitment",
    modes: ["commitment", "recursive-freedom"],
    requiredMode: "commitment",
  },
  ai: {
    id: "ai",
    serverName: "ai-alignment-revisability-audit-remote",
    displayName: "AI Alignment Revisability Audit",
    activationUrl:
      "https://esg-commitment-audit-api.franka328162810.workers.dev/ai-revisability-audit/activate",
    defaultMode: "ai-revisability",
    modes: ["ai-revisability"],
    requiredMode: "ai-revisability",
  },
};

interface McpEnv {
  AUDIT_API: Fetcher;
}

class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

function productDefinition(product: McpProduct): ProductDefinition {
  return PRODUCTS[product];
}

function jsonRpc(request: Request, id: unknown, result: unknown): Response {
  const payload = JSON.stringify({ jsonrpc: "2.0", id, result });
  if ((request.headers.get("accept") || "").includes("text/event-stream")) {
    return new Response(`event: message\ndata: ${payload}\n\n`, {
      headers: {
        "content-type": "text/event-stream; charset=utf-8",
        "cache-control": "no-store",
      },
    });
  }
  return Response.json(JSON.parse(payload));
}

function jsonRpcError(
  request: Request,
  id: unknown,
  code: number,
  message: string,
): Response {
  const payload = JSON.stringify({
    jsonrpc: "2.0",
    id,
    error: { code, message },
  });
  if ((request.headers.get("accept") || "").includes("text/event-stream")) {
    return new Response(`event: message\ndata: ${payload}\n\n`, {
      headers: {
        "content-type": "text/event-stream; charset=utf-8",
        "cache-control": "no-store",
      },
    });
  }
  return Response.json(JSON.parse(payload));
}

function toolResult(value: unknown): Record<string, unknown> {
  return {
    content: [{ type: "text", text: JSON.stringify(value) }],
    structuredContent: value,
    isError: false,
  };
}

function toolError(error: unknown): Record<string, unknown> {
  return {
    content: [
      {
        type: "text",
        text:
          error instanceof Error
            ? `${error.name}: ${error.message}`
            : `Error: ${String(error)}`,
      },
    ],
    isError: true,
  };
}

function toolDefinitions(product: ProductDefinition): Record<string, unknown>[] {
  const tools: Record<string, unknown>[] = [
    {
      name: "get_purchase_options",
      description:
        "Show the current price, checkout, activation, limits, refund, privacy and terms links.",
      inputSchema: {
        type: "object",
        properties: {},
        additionalProperties: false,
      },
      annotations: { readOnlyHint: true },
    },
    {
      name: "get_account",
      description:
        "Show the current plan, quota, billing state, allowed modes and plugin compatibility.",
      inputSchema: {
        type: "object",
        properties: {},
        additionalProperties: false,
      },
      annotations: { readOnlyHint: true },
    },
    {
      name: "audit_text",
      description:
        "Create a hosted audit from text supplied directly in this tool call.",
      inputSchema: {
        type: "object",
        properties: {
          text: { type: "string", maxLength: 2_000_000 },
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
                  enum: PROFILE_VALUES,
                  default: "general",
                },
              }),
        },
        required: ["text"],
        additionalProperties: false,
      },
      annotations: { destructiveHint: false },
    },
    {
      name: "audit_document",
      description:
        "Create a hosted audit from base64 document content. Remote MCP documents are limited to 50 MB decoded.",
      inputSchema: {
        type: "object",
        properties: {
          filename: { type: "string" },
          content_base64: { type: "string" },
          content_type: { type: "string" },
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
                  enum: PROFILE_VALUES,
                  default: "general",
                },
              }),
        },
        required: ["filename", "content_base64", "content_type"],
        additionalProperties: false,
      },
      annotations: { destructiveHint: false },
    },
  ];
  if (product.id === "ai") {
    tools.push({
      name: "audit_evidence_pack",
      description:
        "Create a hosted evidence-pack review from base64 ZIP content. Remote MCP ZIPs are limited to 70 MB compressed; local MCP supports 100 MB.",
      inputSchema: {
        type: "object",
        properties: {
          filename: { type: "string" },
          content_base64: { type: "string" },
        },
        required: ["filename", "content_base64"],
        additionalProperties: false,
      },
      annotations: { destructiveHint: false },
    });
  }
  tools.push(
    {
      name: "get_cloud_audit",
      description:
        "Get a hosted audit status and optionally fetch the completed JSON report.",
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
      name: "delete_cloud_audit",
      description:
        "Delete a hosted audit source and report owned by the API key.",
      inputSchema: {
        type: "object",
        properties: { job_id: { type: "string" } },
        required: ["job_id"],
        additionalProperties: false,
      },
      annotations: { destructiveHint: true },
    },
  );
  return tools;
}

async function apiRequest(
  request: Request,
  env: McpEnv,
  path: string,
  options: {
    method?: string;
    body?: Uint8Array;
    contentType?: string;
    headers?: Record<string, string>;
  } = {},
): Promise<unknown> {
  const authorization = request.headers.get("authorization") || "";
  if (!authorization) throw new ApiError(401, "Missing bearer API key");
  const response = await env.AUDIT_API.fetch(
    new Request(`https://audit-api${path}`, {
      method: options.method || (options.body ? "POST" : "GET"),
      body: options.body,
      headers: {
        Authorization: authorization,
        Accept: "application/json",
        "User-Agent": `ics-remote-mcp/${REMOTE_VERSION}`,
        ...(options.contentType
          ? { "Content-Type": options.contentType }
          : {}),
        ...(options.headers || {}),
      },
      signal: AbortSignal.timeout(240_000),
    }),
  );
  const text = await response.text();
  let payload: { error?: string } = {};
  try {
    payload = text ? JSON.parse(text) : {};
  } catch {
    payload = { error: text.slice(0, 500) };
  }
  if (!response.ok) {
    throw new ApiError(
      response.status,
      payload.error || `Hosted API returned HTTP ${response.status}`,
    );
  }
  return payload;
}

function decodeBase64(value: unknown, maxBytes: number): Uint8Array {
  const raw = String(value || "").replace(/^data:[^;]+;base64,/, "");
  if (!raw) throw new Error("content_base64 is required");
  const padding = raw.endsWith("==") ? 2 : raw.endsWith("=") ? 1 : 0;
  const estimatedBytes = Math.floor((raw.length * 3) / 4) - padding;
  if (estimatedBytes > maxBytes) {
    throw new Error(`Decoded content exceeds the ${maxBytes} byte limit`);
  }
  try {
    return Uint8Array.from(atob(raw), (character) => character.charCodeAt(0));
  } catch {
    throw new Error("content_base64 is not valid base64");
  }
}

async function accountPayload(
  request: Request,
  env: McpEnv,
  product: ProductDefinition,
): Promise<Record<string, unknown>> {
  const account = (await apiRequest(request, env, "/v1/account")) as Record<
    string,
    unknown
  >;
  const allowed = Array.isArray(account.allowed_audit_modes)
    ? account.allowed_audit_modes
    : [];
  return {
    ...account,
    plugin_product: product.id,
    compatible: product.modes.some((mode) => allowed.includes(mode)),
    expected_modes: product.modes,
    activation_url: product.activationUrl,
  };
}

async function ensureMode(
  request: Request,
  env: McpEnv,
  product: ProductDefinition,
  mode: string,
): Promise<void> {
  const account = await accountPayload(request, env, product);
  const allowed = Array.isArray(account.allowed_audit_modes)
    ? account.allowed_audit_modes
    : [];
  if (!allowed.includes(mode)) {
    throw new Error(
      `${product.displayName} cannot run '${mode}' with this API key. ` +
        `Allowed modes: ${allowed.join(", ") || "none"}. Activation: ${product.activationUrl}`,
    );
  }
}

function cleanAiMode(product: ProductDefinition, raw: unknown): string {
  const mode = String(raw || product.defaultMode);
  if (!product.modes.includes(mode)) {
    throw new Error(`Supported modes: ${product.modes.join(", ")}`);
  }
  return mode;
}

async function callTool(
  request: Request,
  env: McpEnv,
  product: ProductDefinition,
  name: string,
  args: Record<string, unknown>,
): Promise<unknown> {
  if (name === "get_purchase_options") {
    const offers = (await apiRequest(request, env, "/v1/offers")) as {
      offers?: Record<string, unknown>[];
    };
    const offer = offers.offers?.find((item) => item.product === product.id);
    if (!offer) throw new Error("No current offer is published");
    return {
      ...offer,
      plugin_product: product.id,
      purchase_steps: [
        "Open checkout_url and complete the monthly subscription.",
        "Keep the Gumroad license key from the receipt.",
        "Open activation_url and activate the license once.",
        "Store the returned API key privately and configure the client.",
        "Call get_account, then retry the audit.",
      ],
    };
  }
  if (name === "get_account") {
    return accountPayload(request, env, product);
  }
  if (name === "audit_text") {
    const text = String(args.text || "");
    if (!text || text.length > 2_000_000) {
      throw new Error("Text must contain between 1 and 2,000,000 characters");
    }
    const mode =
      product.id === "ai"
        ? product.defaultMode
        : cleanAiMode(product, args.mode);
    await ensureMode(request, env, product, mode);
    const fallback = product.id === "ai" ? "ai-policy.txt" : "pasted-text.txt";
    const filename = String(args.filename || fallback);
    return apiRequest(request, env, "/v1/audits", {
      body: new TextEncoder().encode(text),
      contentType:
        filename.toLowerCase().endsWith(".md")
          ? "text/markdown; charset=utf-8"
          : "text/plain; charset=utf-8",
      headers: {
        "X-ESG-Filename": encodeURIComponent(filename),
        "X-ESG-Mode": mode,
        "X-ESG-Profile": String(args.profile || "general"),
        "X-ESG-Weights": String(args.weights || "default"),
      },
    });
  }
  if (name === "audit_document") {
    const filename = String(args.filename || "");
    if (!/\.(pdf|docx|txt|md|markdown)$/i.test(filename)) {
      throw new Error("Remote document filename must be PDF, DOCX, TXT, or Markdown");
    }
    const body = decodeBase64(args.content_base64, MAX_DOCUMENT_BYTES);
    const mode =
      product.id === "ai"
        ? product.defaultMode
        : cleanAiMode(product, args.mode);
    await ensureMode(request, env, product, mode);
    return apiRequest(request, env, "/v1/audits", {
      body,
      contentType: String(args.content_type || "application/octet-stream"),
      headers: {
        "X-ESG-Filename": encodeURIComponent(filename),
        "X-ESG-Mode": mode,
        "X-ESG-Profile": String(args.profile || "general"),
        "X-ESG-Weights": String(args.weights || "default"),
      },
    });
  }
  if (name === "audit_evidence_pack") {
    if (product.id !== "ai") throw new Error("Evidence packs require the AI product");
    const filename = String(args.filename || "evidence-pack.zip");
    if (!filename.toLowerCase().endsWith(".zip")) {
      throw new Error("Evidence-pack filename must end with .zip");
    }
    const body = decodeBase64(args.content_base64, MAX_REMOTE_EVIDENCE_BYTES);
    await ensureMode(request, env, product, "evidence-pack");
    return apiRequest(request, env, "/v1/audits", {
      body,
      contentType: "application/zip",
      headers: {
        "X-ESG-Filename": encodeURIComponent(filename),
        "X-ESG-Mode": "evidence-pack",
      },
    });
  }
  if (name === "get_cloud_audit") {
    const jobId = String(args.job_id || "");
    if (!jobId) throw new Error("job_id is required");
    const status = (await apiRequest(
      request,
      env,
      `/v1/audits/${encodeURIComponent(jobId)}`,
    )) as Record<string, unknown>;
    if (args.include_report && status.status === "completed") {
      status.report = await apiRequest(
        request,
        env,
        `/v1/audits/${encodeURIComponent(jobId)}/report`,
      );
    }
    return status;
  }
  if (name === "delete_cloud_audit") {
    const jobId = String(args.job_id || "");
    if (!jobId) throw new Error("job_id is required");
    await apiRequest(
      request,
      env,
      `/v1/audits/${encodeURIComponent(jobId)}`,
      {
        method: "DELETE",
      },
    );
    return { deleted: true, job_id: jobId };
  }
  throw new Error(`Unknown tool: ${name}`);
}

export async function handleRemoteMcp(
  request: Request,
  env: McpEnv,
  productId: McpProduct,
): Promise<Response> {
  if (request.method !== "POST") {
    return new Response("Streamable HTTP MCP accepts POST requests", {
      status: 405,
      headers: { Allow: "POST" },
    });
  }
  const contentLength = Number(request.headers.get("content-length") || "0");
  if (contentLength > 99 * 1024 * 1024) {
    return Response.json({ error: "MCP request is too large" }, { status: 413 });
  }
  let message: {
    jsonrpc?: string;
    id?: unknown;
    method?: string;
    params?: Record<string, unknown>;
  };
  try {
    message = await request.json();
  } catch {
    return jsonRpcError(request, null, -32700, "Parse error");
  }
  const id = message.id;
  const method = message.method;
  const product = productDefinition(productId);
  if (method === "notifications/initialized" || method === "notifications/cancelled") {
    return new Response(null, { status: 202 });
  }
  if (method === "initialize") {
    return jsonRpc(request, id, {
      protocolVersion: PROTOCOL_VERSION,
      capabilities: { tools: {} },
      serverInfo: { name: product.serverName, version: REMOTE_VERSION },
    });
  }
  if (method === "ping") return jsonRpc(request, id, {});
  if (method === "tools/list") {
    return jsonRpc(request, id, { tools: toolDefinitions(product) });
  }
  if (method !== "tools/call") {
    return jsonRpcError(
      request,
      id,
      -32601,
      `Method not found: ${method}`,
    );
  }
  try {
    const params = message.params || {};
    const value = await callTool(
      request,
      env,
      product,
      String(params.name || ""),
      (params.arguments || {}) as Record<string, unknown>,
    );
    return jsonRpc(request, id, toolResult(value));
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      return Response.json(
        { error: "Missing or invalid bearer API key" },
        { status: 401 },
      );
    }
    return jsonRpc(request, id, toolError(error));
  }
}
