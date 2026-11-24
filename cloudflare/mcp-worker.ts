import { handleRemoteMcp } from "./src/mcp";

interface Env {
  AUDIT_API: Fetcher;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const path = new URL(request.url).pathname.replace(/\/+$/, "") || "/";
    const match = /^\/mcp\/(esg|ai)$/.exec(path);
    if (match) {
      return handleRemoteMcp(request, env, match[1] as "esg" | "ai");
    }
    if (request.method === "GET" && path === "/") {
      return Response.json({
        service: "esg-commitment-audit-mcp",
        version: "0.6.2",
        endpoints: ["/mcp/ai", "/mcp/esg"],
        transport: "Streamable HTTP",
      });
    }
    return Response.json({ error: "Not found" }, { status: 404 });
  },
};
