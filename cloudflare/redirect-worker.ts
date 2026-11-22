import { DurableObject } from "cloudflare:workers";

const NEW_BASE_URL = "https://esg-commitment-audit-api.franka328162810.workers.dev";

export class AuditContainer extends DurableObject {
  fetch(): Response {
    return new Response("This legacy audit object has moved.", { status: 410 });
  }
}

export default {
  fetch(request: Request): Response {
    const incoming = new URL(request.url);
    const target = new URL(incoming.pathname + incoming.search, NEW_BASE_URL);
    return Response.redirect(target.toString(), 308);
  },
  async queue(batch: MessageBatch): Promise<void> {
    batch.ackAll();
  },
  scheduled(): void {
    // The legacy scheduled handlers are retired; the new Worker owns jobs.
  },
};
