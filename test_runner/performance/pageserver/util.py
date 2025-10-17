"""
Utilities used by all code in this sub-directory
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import fixtures.pageserver.many_tenants as many_tenants
from fixtures.log_helper import log
from fixtures.pageserver.utils import wait_until_all_tenants_state

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from fixtures.common_types import TenantId, TimelineId
    from fixtures.serendb_fixtures import (
        SerenDBEnv,
        SerenDBEnvBuilder,
    )


def ensure_pageserver_ready_for_benchmarking(env: SerenDBEnv, n_tenants: int):
    """
    Helper function.
    """
    ps_http = env.pageserver.http_client()

    log.info("wait for all tenants to become active")
    wait_until_all_tenants_state(
        ps_http, "Active", iterations=10 + n_tenants, period=1, http_error_ok=False
    )

    # ensure all layers are resident for predictiable performance
    tenants = [info["id"] for info in ps_http.tenant_list()]
    for tenant in tenants:
        for timeline in ps_http.tenant_status(tenant)["timelines"]:
            info = ps_http.layer_map_info(tenant, timeline)
            for layer in info.historic_layers:
                assert not layer.remote

    env.storage_controller.reconcile_until_idle(timeout_secs=60)

    log.info("ready")


def setup_pageserver_with_tenants(
    serendb_env_builder: SerenDBEnvBuilder,
    name: str,
    n_tenants: int,
    setup: Callable[[SerenDBEnv], tuple[TenantId, TimelineId, dict[str, Any]]],
    timeout_in_seconds: int | None = None,
) -> SerenDBEnv:
    """
    Utility function to set up a pageserver with a given number of identical tenants.
    """

    def doit(serendb_env_builder: SerenDBEnvBuilder) -> SerenDBEnv:
        return many_tenants.single_timeline(serendb_env_builder, setup, n_tenants)

    env = serendb_env_builder.build_and_use_snapshot(name, doit)
    env.start(timeout_in_seconds=timeout_in_seconds)
    ensure_pageserver_ready_for_benchmarking(env, n_tenants)
    return env
