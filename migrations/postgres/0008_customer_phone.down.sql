-- Administrative rollback only: removes phone values. Never run in production without approval.
ALTER TABLE customers DROP COLUMN phone;
