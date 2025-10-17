\echo Use "ALTER EXTENSION serendb UPDATE TO '1.1'" to load this file. \quit

CREATE FUNCTION serendb_get_lfc_stats()
RETURNS SETOF RECORD
AS 'MODULE_PATHNAME', 'serendb_get_lfc_stats'
LANGUAGE C PARALLEL SAFE;

-- Create a view for convenient access.
CREATE VIEW serendb_lfc_stats AS
	SELECT P.* FROM serendb_get_lfc_stats() AS P (lfc_key text, lfc_value bigint);
