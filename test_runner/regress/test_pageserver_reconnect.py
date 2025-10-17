from __future__ import annotations

import threading
import time
from contextlib import closing
from typing import TYPE_CHECKING

import psycopg2.errors
from fixtures.log_helper import log

if TYPE_CHECKING:
    from fixtures.serendb_fixtures import SerenDBEnv, PgBin


# Test updating serendb.pageserver_connstring setting on the fly.
#
# This merely changes some whitespace in the connection string, so
# this doesn't prove that the new string actually takes effect. But at
# least the code gets exercised.
def test_pageserver_reconnect(serendb_simple_env: SerenDBEnv, pg_bin: PgBin):
    env = serendb_simple_env
    env.create_branch("test_pageserver_restarts")
    endpoint = env.endpoints.create_start("test_pageserver_restarts")
    n_reconnects = 1000
    timeout = 0.01
    scale = 10

    def run_pgbench(connstr: str):
        log.info(f"Start a pgbench workload on pg {connstr}")
        pg_bin.run_capture(["pgbench", "-i", "-I", "dtGvp", f"-s{scale}", connstr])
        pg_bin.run_capture(["pgbench", f"-T{int(n_reconnects * timeout)}", connstr])

    thread = threading.Thread(target=run_pgbench, args=(endpoint.connstr(),), daemon=True)
    thread.start()

    with closing(endpoint.connect()) as con:
        with con.cursor() as c:
            c.execute("SELECT setting FROM pg_settings WHERE name='serendb.pageserver_connstring'")
            connstring = c.fetchall()[0][0]
            for i in range(n_reconnects):
                time.sleep(timeout)
                c.execute(
                    "alter system set serendb.pageserver_connstring=%s",
                    (connstring + (" " * (i % 2)),),
                )
                c.execute("select pg_reload_conf()")

    thread.join()


# Test handling errors during page server reconnect
def test_pageserver_reconnect_failure(serendb_simple_env: SerenDBEnv):
    env = serendb_simple_env
    env.create_branch("test_pageserver_reconnect")
    endpoint = env.endpoints.create_start("test_pageserver_reconnect")

    con = endpoint.connect()
    cur = con.cursor()

    cur.execute("set statement_timeout='2s'")
    cur.execute("SELECT setting FROM pg_settings WHERE name='serendb.pageserver_connstring'")
    connstring = cur.fetchall()[0][0]
    cur.execute(
        f"alter system set serendb.pageserver_connstring='{connstring}?some_invalid_param=xyz'"
    )
    cur.execute("select pg_reload_conf()")
    try:
        cur.execute("select count(*) from pg_class")
    except psycopg2.errors.QueryCanceled:
        log.info("Connection to PS failed")
    assert not endpoint.log_contains("ERROR:  cannot wait on socket event without a socket.*")
