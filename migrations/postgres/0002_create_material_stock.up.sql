CREATE TABLE material_stock (
    material_id UUID NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    stock_qty NUMERIC(20,6) NOT NULL,
    unit TEXT NOT NULL,
    is_active BOOLEAN NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT material_stock_name_not_blank
        CHECK (btrim(name) <> ''),
    CONSTRAINT material_stock_nonnegative_quantity
        CHECK (stock_qty >= 0),
    CONSTRAINT material_stock_unit_vocabulary
        CHECK (unit IN ('sheet', 'pcs', 'kg', 'roll', 'pack'))
);
