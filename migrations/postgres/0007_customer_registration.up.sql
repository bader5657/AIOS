-- Minimum Business Authorization P1. Apply with a schema-admin role only.
CREATE TABLE business_owner (
    singleton BOOLEAN PRIMARY KEY DEFAULT TRUE CHECK (singleton),
    telegram_user_id BIGINT NOT NULL UNIQUE CHECK (telegram_user_id > 0),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    verification_evidence TEXT NOT NULL CHECK (length(verification_evidence) > 0),
    approval_reference TEXT NOT NULL CHECK (length(approval_reference) > 0),
    enrolled_by TEXT NOT NULL DEFAULT SESSION_USER,
    enrolled_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    last_draft_message_id BIGINT NOT NULL DEFAULT 0 CHECK (last_draft_message_id >= 0)
);
CREATE TABLE customer_confirmations (
    token TEXT PRIMARY KEY CHECK (token ~ '^[0-9a-f]{64}$'),
    owner_id BIGINT NOT NULL REFERENCES business_owner(telegram_user_id),
    chat_id BIGINT NOT NULL CHECK (chat_id = owner_id),
    message_id BIGINT NOT NULL CHECK (message_id > 0),
    snapshot JSONB NOT NULL CHECK (jsonb_typeof(snapshot) = 'object'),
    created_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL CHECK (expires_at = created_at + INTERVAL '10 minutes'),
    state TEXT NOT NULL CHECK (state IN ('pending', 'superseded', 'consumed')),
    customer_id TEXT UNIQUE REFERENCES customers(customer_id),
    UNIQUE (owner_id, chat_id, message_id),
    CHECK ((state = 'consumed') = (customer_id IS NOT NULL))
);
CREATE UNIQUE INDEX customer_one_pending ON customer_confirmations(owner_id, chat_id)
    WHERE state = 'pending';
CREATE TABLE customer_registration_audit (
    confirmation_token TEXT PRIMARY KEY REFERENCES customer_confirmations(token),
    owner_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL CHECK (chat_id = owner_id),
    customer_id TEXT NOT NULL UNIQUE REFERENCES customers(customer_id),
    snapshot_sha256 TEXT NOT NULL CHECK (snapshot_sha256 ~ '^[0-9a-f]{64}$'),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    action TEXT NOT NULL DEFAULT 'catat_pelanggan' CHECK (action = 'catat_pelanggan')
);
CREATE FUNCTION reject_customer_audit_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'customer registration audit is append-only';
END;
$$;
CREATE TRIGGER customer_audit_immutable
BEFORE UPDATE OR DELETE OR TRUNCATE ON customer_registration_audit
FOR EACH STATEMENT EXECUTE FUNCTION reject_customer_audit_mutation();
REVOKE ALL ON business_owner, customer_confirmations, customer_registration_audit FROM PUBLIC;
