from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

import pytest
from fixtures.utils import subprocess_capture

if TYPE_CHECKING:
    from fixtures.serendb_fixtures import RemotePostgres


@pytest.mark.remote_cluster
@pytest.mark.parametrize(
    "client",
    [
        "csharp/npgsql",
        "java/jdbc",
        "rust/tokio-postgres",
        "python/asyncpg",
        "python/pg8000",
        # PostgresClientKitExample does not support SNI or connection options, so it uses workaround D (https://serendb.com/sni)
        # See example itself: test_runner/pg_clients/swift/PostgresClientKitExample/Sources/PostgresClientKitExample/main.swift
        "swift/PostgresClientKitExample",
        "swift/PostgresNIOExample",
        "typescript/postgresql-client",
        "typescript/serverless-driver",
    ],
)
def test_pg_clients(test_output_dir: Path, remote_pg: RemotePostgres, client: str):
    conn_options = remote_pg.conn_options()

    env_file = None
    with NamedTemporaryFile(mode="w", delete=False) as f:
        env_file = f.name
        f.write(
            f"""
            SERENDB_HOST={conn_options["host"]}
            SERENDB_DATABASE={conn_options["dbname"]}
            SERENDB_USER={conn_options["user"]}
            SERENDB_PASSWORD={conn_options["password"]}
        """
        )

    image_tag = client.lower()
    docker_bin = shutil.which("docker")
    if docker_bin is None:
        raise RuntimeError("docker is required for running this test")

    build_cmd = [docker_bin, "build", "--tag", image_tag, f"{Path(__file__).parent / client}"]
    subprocess_capture(test_output_dir, build_cmd, check=True)

    run_cmd = [docker_bin, "run", "--rm", "--env-file", env_file, image_tag]
    _, output, _ = subprocess_capture(test_output_dir, run_cmd, check=True, capture_stdout=True)

    assert str(output).strip() == "1"
