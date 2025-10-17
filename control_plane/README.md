# Local Development Control Plane (`serendb_local`)

This crate contains tools to start a SerenDB development environment locally. This utility can be used with the `cargo serendb` command.  This is a convenience to invoke
the `serendb_local` binary.

**Note**: this is a dev/test tool -- a minimal control plane suitable for testing
code changes locally, but not suitable for running production systems.

## Example: Start with Postgres 16

To create and start a local development environment with Postgres 16, you will need to provide `--pg-version` flag to 2 of the start-up commands.

```shell
cargo serendb init
cargo serendb start
cargo serendb tenant create --set-default --pg-version 16
cargo serendb endpoint create main --pg-version 16
cargo serendb endpoint start main
```

## Example: Create Test User and Database

By default, `cargo serendb` starts an endpoint with `cloud_admin` and `postgres` database. If you want to have a role and a database similar to what we have on the cloud service, you can do it with the following commands when starting an endpoint.

```shell
cargo serendb endpoint create main --pg-version 16 --update-catalog true
cargo serendb endpoint start main --create-test-user true
```

The first command creates `serendb_superuser` and necessary roles. The second command creates `test` user and `serendb` database. You will see a connection string that connects you to the test user after running the second command.
