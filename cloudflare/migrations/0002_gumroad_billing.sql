ALTER TABLE organizations ADD COLUMN billing_provider TEXT;
ALTER TABLE organizations ADD COLUMN billing_external_id TEXT;
ALTER TABLE organizations ADD COLUMN billing_product_id TEXT;
ALTER TABLE organizations ADD COLUMN billing_status TEXT;
ALTER TABLE organizations ADD COLUMN billing_last_checked_at TEXT;
ALTER TABLE organizations ADD COLUMN gumroad_license_hash TEXT;
ALTER TABLE organizations ADD COLUMN gumroad_license_ciphertext TEXT;
ALTER TABLE organizations ADD COLUMN gumroad_license_iv TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS idx_organizations_billing_external
  ON organizations(billing_provider, billing_external_id)
  WHERE billing_external_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_organizations_gumroad_license
  ON organizations(gumroad_license_hash)
  WHERE gumroad_license_hash IS NOT NULL;
