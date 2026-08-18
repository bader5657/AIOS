CREATE TABLE registry_records (
    record_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    identity_ref TEXT NOT NULL,
    represented_media_type TEXT NOT NULL,
    metadata JSONB NOT NULL,
    relationships JSONB NOT NULL DEFAULT '[]'::jsonb,
    manifest_ref TEXT NOT NULL,
    registration_status TEXT NULL,
    storage_path TEXT NULL,
    source_url TEXT NULL,
    CONSTRAINT registry_records_metadata_object
        CHECK (jsonb_typeof(metadata) = 'object'),
    CONSTRAINT registry_records_relationships_array
        CHECK (jsonb_typeof(relationships) = 'array')
);
