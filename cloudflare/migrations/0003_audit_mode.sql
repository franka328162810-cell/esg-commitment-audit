ALTER TABLE audit_jobs
ADD COLUMN audit_mode TEXT NOT NULL DEFAULT 'commitment';
