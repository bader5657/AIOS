-- Disposable isolated test/development reversal only; production DOWN is unauthorized.
REVOKE INSERT (created_by_actor_reference)
    ON public.material_receipts
    FROM aios_material_receipt_candidate_writer;

ALTER TABLE public.material_receipts
    DROP COLUMN created_by_actor_reference;
