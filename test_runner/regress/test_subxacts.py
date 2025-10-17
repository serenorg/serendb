from __future__ import annotations

from fixtures.serendb_fixtures import (
    SerenDBEnvBuilder,
    check_restored_datadir_content,
)


# Test subtransactions
#
# The pg_subxact SLRU is not preserved on restarts, and doesn't need to be
# maintained in the pageserver, so subtransactions are not very exciting for
# SerenDB. They are included in the commit record though and updated in the
# CLOG.
def test_subxacts(serendb_env_builder: SerenDBEnvBuilder, test_output_dir):
    env = serendb_env_builder.init_start()
    endpoint = env.endpoints.create_start("main")

    pg_conn = endpoint.connect()
    cur = pg_conn.cursor()

    cur.execute("CREATE TABLE t1(i int, j int);")

    cur.execute("select pg_switch_wal();")

    # Issue 100 transactions, with 1000 subtransactions in each.
    for i in range(100):
        cur.execute("begin")
        for j in range(1000):
            cur.execute(f"savepoint sp{j}")
            cur.execute(f"insert into t1 values ({i}, {j})")
        cur.execute("commit")

    check_restored_datadir_content(test_output_dir, env, endpoint)
