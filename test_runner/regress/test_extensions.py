from logging import info

from fixtures.serendb_fixtures import SerenDBEnv


def test_extensions(serendb_simple_env: SerenDBEnv):
    """basic test for the extensions endpoint testing installing extensions"""

    env = serendb_simple_env

    env.create_branch("test_extensions")

    endpoint = env.endpoints.create_start("test_extensions")
    extension = "serendb_test_utils"
    database = "test_extensions"

    endpoint.safe_psql("CREATE DATABASE test_extensions")

    with endpoint.connect(dbname=database) as pg_conn:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT default_version FROM pg_available_extensions WHERE name = 'serendb_test_utils'"
            )
            res = cur.fetchone()
            assert res is not None
            version = res[0]

        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT extname, extversion FROM pg_extension WHERE extname = 'serendb_test_utils'",
            )
            res = cur.fetchone()
            assert not res, "The 'serendb_test_utils' extension is installed"

    client = endpoint.http_client()
    install_res = client.extensions(extension, version, database)

    info("Extension install result: %s", res)
    assert install_res["extension"] == extension and install_res["version"] == version

    with endpoint.connect(dbname=database) as pg_conn:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT extname, extversion FROM pg_extension WHERE extname = 'serendb_test_utils'",
            )
            res = cur.fetchone()
            assert res is not None
            (db_extension_name, db_extension_version) = res

    assert db_extension_name == extension and db_extension_version == version
