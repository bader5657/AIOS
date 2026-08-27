CREATE UNIQUE INDEX material_receipts_source_asset_active_uidx
ON material_receipts (source_asset_reference)
WHERE status NOT IN ('REJECTED', 'CANCELLED');
