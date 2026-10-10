-- Administrative rollback only; never run against production without approval.
DROP TABLE customer_registration_audit;
DROP FUNCTION reject_customer_audit_mutation();
DROP TABLE customer_confirmations;
DROP TABLE business_owner;
