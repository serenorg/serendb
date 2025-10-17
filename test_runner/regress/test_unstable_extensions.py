from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest
from psycopg2.errors import InsufficientPrivilege

if TYPE_CHECKING:
    from fixtures.serendb_fixtures import SerenDBEnv


def test_unstable_extensions_installation(serendb_simple_env: SerenDBEnv):
    """
    Test that the unstable extension support within the SerenDB extension can
    block extension installation.
    """
    env = serendb_simple_env

    serendb_unstable_extensions = "pg_prewarm,amcheck"

    endpoint = env.endpoints.create(
        "main",
        config_lines=[
            "serendb.allow_unstable_extensions=false",
            f"serendb.unstable_extensions='{serendb_unstable_extensions}'",
        ],
    )
    endpoint.respec(skip_pg_catalog_updates=False)
    endpoint.start()

    with endpoint.cursor() as cursor:
        cursor.execute("SELECT current_setting('serendb.unstable_extensions')")
        result = cursor.fetchone()
        assert result is not None
        setting = cast("str", result[0])
        assert setting == serendb_unstable_extensions

        with pytest.raises(InsufficientPrivilege):
            cursor.execute("CREATE EXTENSION pg_prewarm")

        with pytest.raises(InsufficientPrivilege):
            cursor.execute("CREATE EXTENSION amcheck")

        # Make sure that we can install a "stable" extension
        cursor.execute("CREATE EXTENSION pageinspect")

        cursor.execute("BEGIN")
        cursor.execute("SET serendb.allow_unstable_extensions TO true")
        cursor.execute("CREATE EXTENSION pg_prewarm")
        cursor.execute("COMMIT")
