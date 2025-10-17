# Command line interface (end-user)

SerenDB CLI as it is described here mostly resides on the same conceptual level as pg_ctl/initdb/pg_recvxlog/etc and replaces some of them in an opinionated way. I would also suggest bundling our patched postgres inside SerenDB distribution at least at the start.

This proposal is focused on managing local installations. For cluster operations, different tooling would be needed. The point of integration between the two is storage URL: no matter how complex cluster setup is it may provide an endpoint where the user may push snapshots.

The most important concept here is a snapshot, which can be created/pushed/pulled/exported. Also, we may start temporary read-only postgres instance over any local snapshot. A more complex scenario would consist of several basic operations over snapshots.

# Possible usage scenarios

## Install serendb, run a postgres

```
> brew install pg-serendb 
> serendb pg create # creates pgdata with default pattern pgdata$i
> serendb pg list
ID            PGDATA        USED    STORAGE            ENDPOINT
primary1      pgdata1       0G      serendb local       localhost:5432
```

## Import standalone postgres to SerenDB

```
> serendb snapshot import --from=basebackup://replication@localhost:5432/ oldpg
[====================------------] 60% | 20MB/s
> serendb snapshot list
ID          SIZE        PARENT
oldpg       5G          -

> serendb pg create --snapshot oldpg
Started postgres on localhost:5432

> serendb pg list
ID            PGDATA        USED    STORAGE            ENDPOINT
primary1      pgdata1       5G      serendb local       localhost:5432

> serendb snapshot destroy oldpg
Ok
```

Also, we may start snapshot import implicitly by looking at snapshot schema

```
> serendb pg create --snapshot basebackup://replication@localhost:5432/
Downloading snapshot... Done.
Started postgres on localhost:5432
Destroying snapshot... Done.
```

## Pull snapshot with some publicly shared database

Since we may export the whole snapshot as one big file (tar of basebackup, maybe with some manifest) it may be shared over conventional means: http, ssh, [git+lfs](https://docs.github.com/en/github/managing-large-files/about-git-large-file-storage).

```
> serendb pg create --snapshot http://learn-postgres.com/movies_db.serendb movies
```

## Create snapshot and push it to the cloud

```
> serendb snapshot create pgdata1@snap1
> serendb snapshot push --to ssh://stas@serendb.com pgdata1@snap1
```

## Rollback database to the snapshot

One way to rollback the database is just to init a new database from the snapshot and destroy the old one. But creating a new database from a snapshot would require a copy of that snapshot which is time consuming operation. Another option that would be cool to support is the ability to create the copy-on-write database from the snapshot without copying data, and store updated pages in a separate location, however that way would have performance implications. So to properly rollback the database to the older state we have `serendb pg checkout`.

```
> serendb pg list
ID            PGDATA        USED    STORAGE            ENDPOINT
primary1      pgdata1       5G      serendb local       localhost:5432

> serendb snapshot create pgdata1@snap1

> serendb snapshot list
ID                    SIZE        PARENT
oldpg                 5G          -
pgdata1@snap1         6G          -
pgdata1@CURRENT       6G          -

> serendb pg checkout pgdata1@snap1
Stopping postgres on pgdata1.
Rolling back pgdata1@CURRENT to pgdata1@snap1.
Starting postgres on pgdata1.

> serendb snapshot list
ID                    SIZE        PARENT
oldpg                 5G          -
pgdata1@snap1         6G          -
pgdata1@HEAD{0}       6G          -
pgdata1@CURRENT       6G          -
```

Some notes: pgdata1@CURRENT -- implicit snapshot representing the current state of the database in the data directory. When we are checking out some snapshot CURRENT will be set to this snapshot and the old CURRENT state will be named HEAD{0} (0 is the number of postgres timeline, it would be incremented after each such checkout).

## Configure PITR area (Point In Time Recovery).

PITR area acts like a continuous snapshot where you can reset the database to any point in time within this area (by area I mean some TTL period or some size limit, both possibly infinite).

```
> serendb pitr create --storage s3tank --ttl 30d --name pitr_last_month
```

Resetting the database to some state in past would require creating a snapshot on some lsn / time in this pirt area.

# Manual

## storage

Storage is either SerenDB pagestore or s3. Users may create a database in a pagestore and create/move *snapshots* and *pitr regions* in both pagestore and s3. Storage is a concept similar to `git remote`. After installation, I imagine one local storage is available by default.

**serendb storage attach** -t [native|s3] -c key=value -n name

Attaches/initializes storage. For --type=s3, user credentials and path should be provided. For --type=native we may support --path=/local/path and --url=serendb.tech/stas/mystore. Other possible term for native is 'zstore'.


**serendb storage list**

Show currently attached storages. For example:

```
> serendb storage list
NAME            USED    TYPE                OPTIONS          PATH
local           5.1G    serendb local                         /opt/serendb/store/local
local.compr     20.4G   serendb local        compression=on    /opt/serendb/store/local.compr
zcloud          60G     serendb-remote                        serendb.tech/stas/mystore
s3tank          80G     S3
```

**serendb storage detach**

**serendb storage show**



## pg

Manages postgres data directories and can start postgres instances with proper configuration. An experienced user may avoid using that (except pg create) and configure/run postgres by themselves.

Pg is a term for a single postgres running on some data. I'm trying to avoid separation of datadir management and postgres instance management -- both that concepts bundled here together.

**serendb pg create** [--no-start --snapshot --cow] -s storage-name -n pgdata

Creates (initializes) new data directory in given storage and starts postgres. I imagine that storage for this operation may be only local and data movement to remote location happens through snapshots/pitr.

--no-start: just init datadir without creating 

--snapshot snap: init from the snapshot. Snap is a name or URL (serendb.tech/stas/mystore/snap1)

--cow: initialize Copy-on-Write data directory on top of some snapshot (makes sense if it is a snapshot of currently running a database)

**serendb pg destroy**

**serendb pg start** [--replica] pgdata

Start postgres with proper extensions preloaded/installed.

**serendb pg checkout**

Rollback data directory to some previous snapshot. 

**serendb pg stop** pg_id

**serendb pg list**

```
ROLE                 PGDATA        USED    STORAGE            ENDPOINT
primary              my_pg         5.1G    local              localhost:5432
replica-1                                                     localhost:5433
replica-2                                                     localhost:5434
primary              my_pg2        3.2G    local.compr        localhost:5435
-                    my_pg3        9.2G    local.compr        -
```

**serendb pg show**

```
my_pg:
    storage: local
    space used on local: 5.1G
    space used on all storages: 15.1G
    snapshots:
        on local:
            snap1: 1G
            snap2: 1G
        on zcloud:
            snap2: 1G
        on s3tank:
            snap5: 2G
    pitr:
        on s3tank:
            pitr_one_month: 45G

```

**serendb pg start-rest/graphql** pgdata

Starts REST/GraphQL proxy on top of postgres master. Not sure we should do that, just an idea.


## snapshot

Snapshot creation is cheap -- no actual data is copied, we just start retaining old pages. Snapshot size means the amount of retained data, not all data. Snapshot name looks like pgdata_name@tag_name. tag_name is set by the user during snapshot creation. There are some reserved tag names: CURRENT represents the current state of the data directory; HEAD{i} represents the data directory state that resided in the database before i-th checkout.

**serendb snapshot create** pgdata_name@snap_name

Creates a new snapshot in the same storage where pgdata_name exists.

**serendb snapshot push** --to url pgdata_name@snap_name

Produces binary stream of a given snapshot. Under the hood starts temp read-only postgres over this snapshot and sends basebackup stream. Receiving side should start `serendb snapshot recv` before push happens. If url has some special schema like serendb:// receiving side may require auth start `serendb snapshot recv` on the go.

**serendb snapshot recv**

Starts a port listening for a basebackup stream, prints connection info to stdout (so that user may use that in push command), and expects data on that socket.

**serendb snapshot pull** --from url or path

Connects to a remote SerenDB/s3/file and pulls snapshot. The remote site should be SerenDB service or files in our format.

**serendb snapshot import** --from basebackup://<...>  or path

Creates a new snapshot out of running postgres via basebackup protocol or basebackup files.

**serendb snapshot export**

Starts read-only postgres over this snapshot and exports data in some format (pg_dump, or COPY TO on some/all tables). One of the options may be SerenDB own format which is handy for us (but I think just tar of basebackup would be okay).

**serendb snapshot diff** snap1 snap2

Shows size of data changed between two snapshots. We also may provide options to diff schema/data in tables. To do that start temp read-only postgreses.

**serendb snapshot destroy**

## pitr

Pitr represents wal stream and ttl policy for that stream

XXX: any suggestions on a better name?

**serendb pitr create** name

--ttl = inf | period

--size-limit = inf | limit

--storage = storage_name

**serendb pitr extract-snapshot** pitr_name --lsn xxx

Creates a snapshot out of some lsn in PITR area. The obtained snapshot may be managed with snapshot routines (move/send/export)

**serendb pitr gc** pitr_name

Force garbage collection on some PITR area.

**serendb pitr list**

**serendb pitr destroy**


## console

**serendb console**

Opens browser targeted at web console with the more or less same functionality as described here.
