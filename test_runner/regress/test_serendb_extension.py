from __future__ import annotations

import time
from contextlib import closing
from typing import TYPE_CHECKING

from fixtures.log_helper import log

if TYPE_CHECKING:
    from fixtures.serendb_fixtures import SerenDBEnvBuilder


# Verify that the SerenDB extension is installed and has the correct version.
def test_serendb_extension(serendb_env_builder: SerenDBEnvBuilder):
    env = serendb_env_builder.init_start()
    env.create_branch("test_create_extension_serendb")

    endpoint_main = env.endpoints.create("test_create_extension_serendb")
    # don't skip pg_catalog updates - it runs CREATE EXTENSION serendb
    endpoint_main.respec(skip_pg_catalog_updates=False)
    endpoint_main.start()

    with closing(endpoint_main.connect()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT extversion from pg_extension where extname='serendb'")
            # If this fails, it means the extension is either not installed
            # or was updated and the version is different.
            #
            # IMPORTANT:
            # If the version has changed, the test should be updated.
            # Ensure that the default version is also updated in the serendb.control file
            assert cur.fetchone() == ("1.6",)
            cur.execute("SELECT * from serendb.SERENDB_STAT_FILE_CACHE")
            res = cur.fetchall()
            log.info(res)
            assert len(res) == 1
            assert len(res[0]) == 5


# Verify that the SerenDB extension can be upgraded/downgraded.
def test_serendb_extension_compatibility(serendb_env_builder: SerenDBEnvBuilder):
    env = serendb_env_builder.init_start()
    env.create_branch("test_serendb_extension_compatibility")

    endpoint_main = env.endpoints.create("test_serendb_extension_compatibility")
    # don't skip pg_catalog updates - it runs CREATE EXTENSION serendb
    endpoint_main.respec(skip_pg_catalog_updates=False)
    endpoint_main.start()

    with closing(endpoint_main.connect()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT extversion from pg_extension where extname='serendb'")
            # IMPORTANT:
            # If the version has changed, the test should be updated.
            # Ensure that the default version is also updated in the serendb.control file
            assert cur.fetchone() == ("1.6",)
            cur.execute("SELECT * from serendb.SERENDB_STAT_FILE_CACHE")
            all_versions = ["1.6", "1.5", "1.4", "1.3", "1.2", "1.1", "1.0"]
            current_version = "1.6"
            for idx, begin_version in enumerate(all_versions):
                for target_version in all_versions[idx + 1 :]:
                    if current_version != begin_version:
                        cur.execute(
                            f"ALTER EXTENSION serendb UPDATE TO '{begin_version}'; -- {current_version}->{begin_version}"
                        )
                        current_version = begin_version
                    # downgrade
                    cur.execute(
                        f"ALTER EXTENSION serendb UPDATE TO '{target_version}'; -- {begin_version}->{target_version}"
                    )
                    # upgrade
                    cur.execute(
                        f"ALTER EXTENSION serendb UPDATE TO '{begin_version}'; -- {target_version}->{begin_version}"
                    )


# Verify that the SerenDB extension can be auto-upgraded to the latest version.
def test_serendb_extension_auto_upgrade(serendb_env_builder: SerenDBEnvBuilder):
    env = serendb_env_builder.init_start()
    env.create_branch("test_serendb_extension_auto_upgrade")

    endpoint_main = env.endpoints.create("test_serendb_extension_auto_upgrade")
    # don't skip pg_catalog updates - it runs CREATE EXTENSION serendb
    endpoint_main.respec(skip_pg_catalog_updates=False)
    endpoint_main.start()

    with closing(endpoint_main.connect()) as conn:
        with conn.cursor() as cur:
            cur.execute("ALTER EXTENSION serendb UPDATE TO '1.0';")
            cur.execute("SELECT extversion from pg_extension where extname='serendb'")
            assert cur.fetchone() == ("1.0",)  # Ensure the extension gets downgraded

    endpoint_main.stop()
    time.sleep(1)
    endpoint_main.start()
    time.sleep(1)

    with closing(endpoint_main.connect()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT extversion from pg_extension where extname='serendb'")
            assert cur.fetchone() != ("1.0",)  # Ensure the extension gets upgraded
