-- Additive: existing rows and legacy writers retain NULL phone.
ALTER TABLE customers ADD COLUMN phone TEXT NULL;
