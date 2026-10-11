# Assignment 2 local PostgreSQL package

Read [the assignment](assignment.md), then follow [the experiment protocol](docs/experiment-protocol.md).
Use pgAdmin (included), DBeaver, or PyCharm to write and run your SQL. Keep your SQL and one investigation report
in a convenient local folder; `submission/` contains optional starters.

## First start

Install Docker Desktop on Windows/macOS, or Docker Engine with Compose v2 on Linux. Use Linux containers.
Download or clone the assignment materials from GitHub. If you download a ZIP, extract it into a writable folder.
Open a terminal in the Assignment 2 folder containing `compose.yaml`.

Start Docker and keep an internet connection for the first run. Run these two commands:

```sh
docker compose up -d --wait db pgadmin
docker compose run --rm --build tools reset --profile default
```

Docker downloads the required images, builds the setup tool, and loads the bundled data. The first run can take
several minutes. Wait for each command to finish successfully; setup prints the selected profile and row counts.
The defaults work without a `.env` file. No host Python installation is needed.

For a smaller dataset, use `--profile reduced` in the reset command. Both profiles have the same tasks and marking.
Keep one profile throughout a before/after experiment. To intentionally switch an already loaded database, use:

```sh
docker compose run --rm tools reset --profile reduced --allow-profile-change
```

A same-profile reset restores a clean baseline and removes your added indexes. It keeps your local SQL and report
files. For changed ports or a second independent copy, see [troubleshooting](docs/troubleshooting.md).

## Connect and work

Open pgAdmin at `http://127.0.0.1:55051` and sign in with:

- Email: `student@course.local`
- Password: `assignment-2-pgadmin-password`

Open the supplied Assignment 2 server and enter database password `assignment-2-local-password`.
Its connection inside Docker uses host `db`, port `5432`, database `assignment2`, and user `student`.
Open Query Tool for that database.

For DBeaver or PyCharm, create a PostgreSQL connection with host `127.0.0.1`, port `55433`, database `assignment2`,
user `student`, and password `assignment-2-local-password`.

Enable autocommit. At the start of every SQL session, run:

```sql
SET timezone = 'UTC';
```

Write your hypotheses in your report before measuring. Follow the [protocol](docs/experiment-protocol.md) for the
baseline runs, scratch reset, indexes, and indexed runs. Use [SQL guidance](docs/sql-guide.md) for row counts and
sizes, and the [data dictionary](docs/data-dictionary.md) for the fixed inputs.

## Submit and stop

Submit your SQL, one report, and readable plans as explained in [the assignment](assignment.md).
The [submission guide](submission/README.md) gives a short checklist. Google Docs, Word, Markdown, and PDF reports
are all suitable; export Google Docs to PDF for a stable Moodle submission.

When finished working, stop the services:

```sh
docker compose stop
```

This keeps the database and your work. Start it again with the first command above; run reset only when you need
a fresh baseline.
