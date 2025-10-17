SerenDB CLI allows you to operate database clusters (catalog clusters) and their commit history locally and in the cloud. Since ANSI calls them catalog clusters and cluster is a loaded term in the modern infrastructure we will call it "catalog".

# CLI v2 (after chatting with Carl)

SerenDB introduces the notion of a repository.

```bash
serendb init
serendb clone serendb://serendb.io/piedpiper/northwind -- clones a repo to the northwind directory
```

Once you have a cluster catalog you can explore it

```bash
serendb log -- returns a list of commits
serendb status -- returns if there are changes in the catalog that can be committed
serendb commit -- commits the changes and generates a new commit hash
serendb branch experimental <hash> -- creates a branch called testdb based on a given commit hash
```

To make changes in the catalog you need to run compute nodes

```bash
-- here is how you a compute node
serendb start /home/pipedpiper/northwind:main -- starts a compute instance
serendb start serendb://serendb.com/northwind:main -- starts a compute instance in the cloud
-- you can start a compute node against any hash or branch
serendb start /home/pipedpiper/northwind:experimental --port 8008 -- start another compute instance (on different port)
-- you can start a compute node against any hash or branch
serendb start /home/pipedpiper/northwind:<hash> --port 8009 -- start another compute instance (on different port)

-- After running some DML you can run 
-- serendb status and see how there are two WAL streams one on top of 
-- the main branch
serendb status 
-- and another on top of the experimental branch
serendb status -b experimental

-- you can commit each branch separately
serendb commit main
-- or
serendb commit -c /home/pipedpiper/northwind:experimental
```

Starting compute instances against cloud environments

```bash
-- you can start a compute instance against the cloud environment
-- in this case all of the changes will be streamed into the cloud
serendb start https://serendb.com/pipedpiper/northwind:main
serendb start https://serendb.com/pipedpiper/northwind:main
serendb status -c https://serendb.com/pipedpiper/northwind:main
serendb commit -c https://serendb.com/pipedpiper/northwind:main
serendb branch -c https://serendb.com/pipedpiper/northwind:<hash> experimental
```

Pushing data into the cloud

```bash
-- pull all the commits from the cloud
serendb pull
-- push all the commits to the cloud
serendb push
```
