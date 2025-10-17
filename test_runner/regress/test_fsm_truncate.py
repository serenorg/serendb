from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fixtures.serendb_fixtures import SerenDBEnvBuilder


def test_fsm_truncate(serendb_env_builder: SerenDBEnvBuilder):
    env = serendb_env_builder.init_start()
    env.create_branch("test_fsm_truncate")
    endpoint = env.endpoints.create_start("test_fsm_truncate")
    endpoint.safe_psql(
        "CREATE TABLE t1(key int); CREATE TABLE t2(key int); TRUNCATE TABLE t1; TRUNCATE TABLE t2;"
    )
