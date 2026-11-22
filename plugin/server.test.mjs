import assert from "node:assert/strict";
import test from "node:test";

import { handleMessage } from "./server.mjs";

test("plugin initializes as an MCP tool server", async () => {
  const response = await handleMessage({
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: { protocolVersion: "2025-06-18" },
  });
  assert.equal(response.result.serverInfo.name, "esg-commitment-audit");
  assert.equal(response.result.capabilities.tools !== undefined, true);
});

test("plugin exposes hosted audit tools", async () => {
  const response = await handleMessage({
    jsonrpc: "2.0",
    id: 2,
    method: "tools/list",
  });
  const names = new Set(response.result.tools.map((tool) => tool.name));
  assert.deepEqual(
    [...names].sort(),
    [
      "audit_document",
      "audit_text",
      "delete_cloud_audit",
      "get_account",
      "get_cloud_audit",
    ],
  );
});
