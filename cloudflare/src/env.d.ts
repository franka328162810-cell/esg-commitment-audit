interface Env {
  ICS_INTERNAL_TOKEN: string;
  ICS_ADMIN_TOKEN: string;
  ICS_STRIPE_WEBHOOK_SECRET?: string;
  ICS_GENERIC_WEBHOOK_SECRET?: string;
  STRIPE_SECRET_KEY?: string;
  STRIPE_PRICE_STARTER?: string;
  STRIPE_PRICE_PRO?: string;
}
