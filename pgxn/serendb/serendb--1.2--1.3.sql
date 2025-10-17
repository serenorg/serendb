\echo Use "ALTER EXTENSION serendb UPDATE TO '1.3'" to load this file. \quit

CREATE FUNCTION approximate_working_set_size(reset bool)
RETURNS integer
AS 'MODULE_PATHNAME', 'approximate_working_set_size'
LANGUAGE C PARALLEL SAFE;

GRANT EXECUTE ON FUNCTION approximate_working_set_size(bool) TO pg_monitor;

