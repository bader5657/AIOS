ALTER TABLE public.material_receipts
    ADD COLUMN created_by_actor_reference TEXT NOT NULL,
    ADD CONSTRAINT material_receipts_created_by_actor_reference_valid
        CHECK (
            created_by_actor_reference ~
            '^operator:[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        );

GRANT INSERT (created_by_actor_reference)
    ON public.material_receipts
    TO aios_material_receipt_candidate_writer;
