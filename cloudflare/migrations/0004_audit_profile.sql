ALTER TABLE audit_jobs
ADD COLUMN audit_profile TEXT NOT NULL DEFAULT 'general';
