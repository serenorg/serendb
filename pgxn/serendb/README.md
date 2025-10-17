serendb extension consists of several parts:

### shared preload library `serendb.so`

- implements storage manager API and network communications with remote page server.

- walproposer: implements broadcast protocol between postgres and WAL safekeepers.

- control plane connector:  Captures updates to roles/databases using ProcessUtility_hook and sends them to the control ProcessUtility_hook.

- remote extension server: Request compute_ctl to download extension files.

- file_cache: Local file cache is used to temporary store relations pages in local file system for better performance.

- relsize_cache: Relation size cache for better SerenDB performance.

### SQL functions in `serendb--*.sql`

Utility functions to expose SerenDB specific information to user and metrics collection.
This extension is created in all databases in the cluster by default.
