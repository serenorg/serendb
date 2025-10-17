DO $$
BEGIN
    IF (SELECT pg_catalog.current_setting('server_version_num')::pg_catalog.numeric < 160000) THEN
        RETURN;
    END IF;

    IF NOT (SELECT pg_catalog.pg_has_role('serendb_superuser', 'pg_create_subscription', 'member')) THEN
        RAISE EXCEPTION 'serendb_superuser cannot execute pg_create_subscription';
    END IF;
END $$;
