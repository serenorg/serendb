# Communicator

This package provides the so-called "compute-pageserver communicator",
or just "communicator" in short. The communicator is a separate
background worker process that runs in the PostgreSQL server. It's
part of the serendb extension. Currently, it only provides an HTTP
endpoint for metrics, but in the future it will evolve to handle all
communications with the pageservers.

## Source code view

pgxn/serendb/communicator_process.c
    Contains code needed to start up the communicator process, and
    the glue that interacts with PostgreSQL code and the Rust
    code in the communicator process.


pgxn/serendb/communicator/src/worker_process/
    Worker process main loop and glue code

At compilation time, pgxn/serendb/communicator/ produces a static
library, libcommunicator.a. It is linked to the serendb.so extension
library.
