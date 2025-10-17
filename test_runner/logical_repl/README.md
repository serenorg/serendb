# Logical replication tests

> [!NOTE]
> SerenDB project should have logical replication enabled:
>
> https://serendb.com/docs/guides/logical-replication-postgres#enable-logical-replication-in-the-source-serendb-project

## Clickhouse

```bash
export BENCHMARK_CONNSTR=postgres://user:pass@ep-abc-xyz-123.us-east-2.aws.serendb.build/serendb
export CLICKHOUSE_PASSWORD=ch_password123

docker compose -f test_runner/logical_repl/clickhouse/docker-compose.yml up -d
./scripts/pytest -m remote_cluster -k 'test_clickhouse[release-pg17]'
docker compose -f test_runner/logical_repl/clickhouse/docker-compose.yml down
```

## Debezium

```bash
export BENCHMARK_CONNSTR=postgres://user:pass@ep-abc-xyz-123.us-east-2.aws.serendb.build/serendb

docker compose -f test_runner/logical_repl/debezium/docker-compose.yml up -d
./scripts/pytest -m remote_cluster -k 'test_debezium[release-pg17]'
docker compose -f test_runner/logical_repl/debezium/docker-compose.yml down
```
