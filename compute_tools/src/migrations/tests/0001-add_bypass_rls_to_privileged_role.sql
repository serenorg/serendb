DO $$
DECLARE
    bypassrls boolean;
BEGIN
    SELECT rolbypassrls INTO bypassrls FROM pg_catalog.pg_roles WHERE rolname = 'serendb_superuser';
    IF NOT bypassrls THEN
        RAISE EXCEPTION 'serendb_superuser cannot bypass RLS';
    END IF;
END $$;
