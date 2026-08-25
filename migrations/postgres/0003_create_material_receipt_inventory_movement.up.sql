CREATE TABLE material_receipts (
    receipt_id UUID NOT NULL PRIMARY KEY,
    supplier_name TEXT NOT NULL,
    document_number TEXT NULL,
    document_date DATE NULL,
    received_at TIMESTAMPTZ NOT NULL,
    source_asset_reference TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'EXTRACTED',
    version INTEGER NOT NULL DEFAULT 1,
    confirmed_version INTEGER NULL,
    confirmed_at TIMESTAMPTZ NULL,
    confirmation_actor_reference TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT material_receipts_supplier_name_valid
        CHECK (
            btrim(supplier_name) <> ''
            AND char_length(supplier_name) <= 128
        ),
    CONSTRAINT material_receipts_document_number_valid
        CHECK (
            document_number IS NULL
            OR (
                document_number = btrim(document_number)
                AND document_number <> ''
                AND char_length(document_number) <= 128
            )
        ),
    CONSTRAINT material_receipts_source_asset_reference_not_blank
        CHECK (btrim(source_asset_reference) <> ''),
    CONSTRAINT material_receipts_status_valid
        CHECK (
            status IN (
                'EXTRACTED',
                'NEEDS_REVIEW',
                'CONFIRMED',
                'POSTED',
                'REJECTED',
                'CANCELLED'
            )
        ),
    CONSTRAINT material_receipts_version_valid
        CHECK (
            version > 0
            AND (
                confirmed_version IS NULL
                OR (
                    confirmed_version > 0
                    AND confirmed_version <= version
                )
            )
        ),
    CONSTRAINT material_receipts_confirmation_complete_or_absent
        CHECK (
            (
                confirmed_version IS NULL
                AND confirmed_at IS NULL
                AND confirmation_actor_reference IS NULL
            )
            OR (
                confirmed_version IS NOT NULL
                AND confirmed_at IS NOT NULL
                AND confirmation_actor_reference IS NOT NULL
                AND btrim(confirmation_actor_reference) <> ''
            )
        ),
    CONSTRAINT material_receipts_authoritative_confirmation_valid
        CHECK (
            status NOT IN ('CONFIRMED', 'POSTED')
            OR (
                confirmed_version = version
                AND confirmed_at IS NOT NULL
                AND confirmation_actor_reference IS NOT NULL
            )
        ),
    CONSTRAINT material_receipts_candidate_unconfirmed
        CHECK (
            status NOT IN ('EXTRACTED', 'NEEDS_REVIEW')
            OR (
                confirmed_version IS NULL
                AND confirmed_at IS NULL
                AND confirmation_actor_reference IS NULL
            )
        )
);

CREATE TABLE material_receipt_items (
    receipt_item_id UUID NOT NULL PRIMARY KEY,
    receipt_id UUID NOT NULL,
    line_number INTEGER NOT NULL,
    candidate_material_description TEXT NULL,
    canonical_display_name TEXT NULL,
    size_description TEXT NULL,
    specification TEXT NULL,
    material_id UUID NULL,
    full_colly_count INTEGER NOT NULL DEFAULT 0,
    qty_per_full_colly NUMERIC(20,6) NULL,
    partial_qty NUMERIC(20,6) NOT NULL DEFAULT 0,
    total_qty NUMERIC(20,6) NOT NULL,
    unit TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'EXTRACTED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT material_receipt_items_receipt_fk
        FOREIGN KEY (receipt_id)
        REFERENCES material_receipts(receipt_id)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT material_receipt_items_material_fk
        FOREIGN KEY (material_id)
        REFERENCES material_stock(material_id)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT material_receipt_items_receipt_line_unique
        UNIQUE (receipt_id, line_number),
    CONSTRAINT material_receipt_items_line_positive
        CHECK (line_number > 0),
    CONSTRAINT material_receipt_items_candidate_description_valid
        CHECK (
            candidate_material_description IS NULL
            OR btrim(candidate_material_description) <> ''
        ),
    CONSTRAINT material_receipt_items_canonical_name_valid
        CHECK (
            canonical_display_name IS NULL
            OR btrim(canonical_display_name) <> ''
        ),
    CONSTRAINT material_receipt_items_size_valid
        CHECK (
            size_description IS NULL
            OR btrim(size_description) <> ''
        ),
    CONSTRAINT material_receipt_items_specification_valid
        CHECK (
            specification IS NULL
            OR btrim(specification) <> ''
        ),
    CONSTRAINT material_receipt_items_full_colly_nonnegative
        CHECK (full_colly_count >= 0),
    CONSTRAINT material_receipt_items_qty_per_colly_semantics
        CHECK (
            (
                full_colly_count = 0
                AND qty_per_full_colly IS NULL
            )
            OR (
                full_colly_count > 0
                AND qty_per_full_colly > 0
            )
        ),
    CONSTRAINT material_receipt_items_partial_qty_nonnegative
        CHECK (partial_qty >= 0),
    CONSTRAINT material_receipt_items_total_qty_positive
        CHECK (total_qty > 0),
    CONSTRAINT material_receipt_items_packaging_formula
        CHECK (
            total_qty =
                (full_colly_count * COALESCE(qty_per_full_colly, 0))
                + partial_qty
        ),
    CONSTRAINT material_receipt_items_unit_valid
        CHECK (unit IN ('sheet', 'pcs', 'kg', 'roll', 'pack')),
    CONSTRAINT material_receipt_items_sheet_quantities_integral
        CHECK (
            unit <> 'sheet'
            OR (
                (
                    qty_per_full_colly IS NULL
                    OR qty_per_full_colly = trunc(qty_per_full_colly)
                )
                AND partial_qty = trunc(partial_qty)
                AND total_qty = trunc(total_qty)
            )
        ),
    CONSTRAINT material_receipt_items_status_valid
        CHECK (
            status IN (
                'EXTRACTED',
                'NEEDS_REVIEW',
                'CONFIRMED',
                'POSTED',
                'REJECTED',
                'CANCELLED'
            )
        ),
    CONSTRAINT material_receipt_items_resolved_when_authoritative
        CHECK (
            status NOT IN ('CONFIRMED', 'POSTED')
            OR material_id IS NOT NULL
        )
);

CREATE TABLE inventory_movements (
    movement_id UUID NOT NULL PRIMARY KEY,
    material_id UUID NOT NULL,
    movement_type TEXT NOT NULL,
    quantity_delta NUMERIC(20,6) NOT NULL,
    unit TEXT NOT NULL,
    source_receipt_item_id UUID NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    posted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    posting_actor_reference TEXT NOT NULL,
    balance_before NUMERIC(20,6) NOT NULL,
    balance_after NUMERIC(20,6) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT inventory_movements_material_fk
        FOREIGN KEY (material_id)
        REFERENCES material_stock(material_id)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT inventory_movements_source_item_fk
        FOREIGN KEY (source_receipt_item_id)
        REFERENCES material_receipt_items(receipt_item_id)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT inventory_movements_source_item_unique
        UNIQUE (source_receipt_item_id),
    CONSTRAINT inventory_movements_type_valid
        CHECK (movement_type IN ('RECEIPT')),
    CONSTRAINT inventory_movements_quantity_positive
        CHECK (quantity_delta > 0),
    CONSTRAINT inventory_movements_unit_valid
        CHECK (unit IN ('sheet', 'pcs', 'kg', 'roll', 'pack')),
    CONSTRAINT inventory_movements_actor_not_blank
        CHECK (btrim(posting_actor_reference) <> ''),
    CONSTRAINT inventory_movements_balances_nonnegative
        CHECK (
            balance_before >= 0
            AND balance_after >= 0
        ),
    CONSTRAINT inventory_movements_balance_formula
        CHECK (balance_after = balance_before + quantity_delta),
    CONSTRAINT inventory_movements_sheet_quantities_integral
        CHECK (
            unit <> 'sheet'
            OR (
                quantity_delta = trunc(quantity_delta)
                AND balance_before = trunc(balance_before)
                AND balance_after = trunc(balance_after)
            )
        )
);

CREATE INDEX material_receipts_status_idx
    ON material_receipts (status);

CREATE INDEX material_receipts_document_lookup_idx
    ON material_receipts (supplier_name, document_number)
    WHERE document_number IS NOT NULL;

CREATE INDEX material_receipts_source_asset_idx
    ON material_receipts (source_asset_reference);

CREATE INDEX material_receipt_items_material_idx
    ON material_receipt_items (material_id)
    WHERE material_id IS NOT NULL;

CREATE INDEX inventory_movements_material_posted_idx
    ON inventory_movements (material_id, posted_at DESC);
