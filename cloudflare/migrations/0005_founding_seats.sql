CREATE TABLE IF NOT EXISTS founding_seats (
  product_id TEXT NOT NULL,
  seat_number INTEGER NOT NULL,
  organization_id TEXT NOT NULL UNIQUE,
  license_hash TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  PRIMARY KEY (product_id, seat_number)
);
