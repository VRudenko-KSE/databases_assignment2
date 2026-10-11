# Troubleshooting

Start with [setup](../README.md) and [the experiment protocol](experiment-protocol.md).
If a setup command fails, check that Docker is running and inspect:

```sh
docker compose ps
docker compose logs db pgadmin
```

Keep the error message when asking staff for help. Do not include local passwords.

## Ports, paths, and connections

Run Compose from the package folder containing `compose.yaml`. Quote paths containing spaces.
If a port is occupied, copy `.env.example` to `.env`, change `POSTGRES_PORT` or `PGADMIN_PORT`, and rerun the start
command. Use the selected port in your browser or host SQL client. The defaults are `55051` for pgAdmin and
`55433` for PostgreSQL.

Host SQL clients connect to `127.0.0.1`; the supplied pgAdmin server connects inside Docker to `db:5432`.
Use database `assignment2`, user `student`, and the database password from the README. The pgAdmin website login
is separate from the database password. Wait for the start command to complete before connecting.

The Compose file has a fixed default project name, so two extracted copies normally share database volumes.
For an independent copy, set different host ports in that copy's `.env`, choose a new project name, and use it
in every command, for example:

```sh
docker compose -p a2-second-copy up -d --wait db pgadmin
docker compose -p a2-second-copy run --rm --build tools reset --profile default
```

## Downloads and setup

The first start needs internet access to download images and build the setup tool. If that fails, check Docker's
network/proxy settings and repeat the failed command. The dataset is already included in the package.
If Docker cannot find the tools image, repeat the README's reset command with `--build`.
A successful reset prints the profile and row counts; do not continue from a failed setup.

## SQL results and failed experiments

Run `SET timezone = 'UTC';` in each SQL session and keep autocommit on. In pgAdmin, run the textual
`EXPLAIN (ANALYZE, BUFFERS)` statement using ordinary Execute to inspect the plan output.
When a script contains several SELECTs, run each complete SELECT separately to inspect every result grid.

If INSERT has run but saving the plan fails, it may already be committed. Rebuild scratch with `reset-write`,
reapply the appropriate scratch indexes, and begin a new labelled write attempt. Never rerun INSERT in place.
For a failed or incomparable full pair, keep your notes and use same-profile `reset` for a clean baseline.
Reset commands keep your local SQL and report files.

If a query is slow, first check its joins, date bounds, filters, and plan. A broad report may legitimately use a
sequential scan; no particular scan or speedup is required. If your client imposes a timeout that interrupts a
valid query, adjust it consistently for both configurations and note the change in your report.

Matching before/after results may still be wrong. Recheck grain, exclusive ends, quiet dates, rank peers, and the
running window frame. The [SQL guide](sql-guide.md) lists the required correctness checks.

If reset reports unexpected objects or dependencies, keep the diagnostic and ask staff for help, or use a fresh
independent copy. Do not remove unrelated course objects to make reset succeed.
