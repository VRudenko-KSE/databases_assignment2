# Before/after experiment protocol

Complete [setup](../README.md), write your SQL, and record your hypotheses and workload priorities in your report
before measuring. Use one profile and the same SQL, fixed parameters, data, and execution settings in both
configurations. Keep UTC and autocommit enabled. Leave the supplied PostgreSQL settings unchanged.

`baseline` has the supplied primary keys and constraints but no student-created indexes. `indexed` adds your final
portfolio of at most three designs, including a composite-order investigation. Explore first if needed, then reset
before the final comparison. Keep the same final portfolio throughout indexed reads and INSERT.

## 1. Prepare a clean baseline

If you have just completed setup and have not changed the data or added indexes, your baseline is ready.
Otherwise, reset the assignment data from the package folder:

```sh
docker compose run --rm tools reset --profile default
```

Use `reduced` instead of `default` in every command if that is your chosen profile. Setup prints the profile and
initial counts. It restores historical rows in both `mobility.events` and the logged scratch table `a2_write.events`,
with constraints intact and no student-added indexes. Your local work files are kept.

In your SQL client, run:

```sql
SET timezone = 'UTC';
ANALYZE mobility.stations;
ANALYZE mobility.events;
ANALYZE mobility.ingest_batch;
ANALYZE a2_write.events;
```

Record the profile, initial historical row count, and batch row count in your report. Default has 1,000,000 historical
rows and a 10,000-row batch; reduced has 100,000 and 1,000. Use the simple count queries in
[SQL guidance](sql-guide.md). Open and run [sizes.sql](../runtime/sql/sizes.sql) in your client and record the
baseline canonical table/index sizes in your report.

## 2. Measure baseline reads

Run R1, R2, R3, and R4 once each, in that order, as a warm-up. Inspect the actual results for correctness.
Then run each report in the same order with:

```sql
EXPLAIN (ANALYZE, BUFFERS)
-- Your complete SELECT goes here.
```

This command executes the SELECT and returns a text plan. Save each complete plan in your report or an attachment,
labelled with the report and `baseline`. In pgAdmin use Query Tool's ordinary Execute action for the SQL above;
copy the Query Plan rows from the result grid. DBeaver and PyCharm can run the same SQL in their SQL editors.
Copied text, JSON if you prefer it, and legible GUI screenshots are acceptable. Preserve the node details, timing,
and buffer observations needed for your analysis. A screenshot must show readable evidence, not only a plan overview.

EXPLAIN displays execution work rather than the report's returned values. Check the actual SELECT results separately:
required columns and ordering, row counts, boundaries, quiet dates, ties, and cross-report reconciliation. Record
checks and observations in the report. You may save result exports for your own comparison; they are not mandatory.

## 3. Measure baseline INSERT once

Your INSERT must copy `mobility.ingest_batch` into `a2_write.events`, with explicit target columns and source rows
ordered by `event_id`. Keep the canonical `mobility.events` table unchanged.

1. Run `SELECT count(*) FROM a2_write.events;` once as a read-only warm-up and record this before-count.
   It must equal the profile's historical count.
2. Run `sizes.sql` and record scratch table/index sizes before INSERT.
3. With autocommit on, execute `EXPLAIN (ANALYZE, BUFFERS)` followed by your INSERT **once** and save its baseline plan.
4. Count scratch rows again and record sizes again. Count growth must equal the supplied batch count:
   1,000,000 → 1,010,000 for default, or 100,000 → 101,000 for reduced.
   Explain why your statement copies the batch once, and verify the canonical row count remains unchanged.

**EXPLAIN ANALYZE executes and commits the INSERT when autocommit is on.** Do not execute a second plain INSERT
for a row count, and never warm up with INSERT. The INSERT plan's output-row count may not be the inserted-row count;
use the before/after table counts. Copying data, building indexes, and ANALYZE are outside the measured execution.

## 4. Rebuild scratch and install the portfolio

Before indexed INSERT, rebuild scratch from the original historical rows:

```sh
docker compose run --rm tools reset-write --profile default
```

This rebuilds the logged scratch table and its constraints in the same initial row order. Deleting the batch does
not restore comparable physical state. It leaves the canonical table available for the read experiment.

Execute your final canonical and scratch index blocks in your SQL client. Scratch definitions must match the
canonical designs exactly: columns, order/direction, expressions, predicates, and included columns if used.
Scratch copies do not count as extra designs. Remove rejected exploratory indexes before the final pair.
Run the four ANALYZE statements from step 1 again, then record indexed canonical table/index sizes and each
individual index's size.

## 5. Measure indexed reads and INSERT

Repeat step 2's warm-up and plan sequence with the same R1–R4 SQL and parameters. Save plans labelled `indexed`,
and inspect the report results again. Adding indexes must not change the required values, duplicates, or order.

Repeat step 3 with the rebuilt scratch table and matching indexes: count warm-up, before sizes, one measured
INSERT, then after count and sizes. Keep the same portfolio through all five indexed measurements.

If a SQL error occurs, stop and resolve it. If INSERT may already have executed, rebuild scratch before retrying
and reapply its matching indexes. If the whole pair has become incomparable, start again from a clean baseline.
Label repeat attempts and discuss variation; do not choose only the fastest run as your evidence.

## 6. Explain the comparisons in one report

You now have ten plans: a baseline and indexed plan for each of R1–R4 and INSERT. Compare every pair using a table
and your own causal explanation. Five rows with before/after columns are recommended; ten rows with one row per
operation/configuration are also acceptable. Include time, relevant buffer hits/reads, main plan changes, and clear
references to the supporting plans. Explain estimated/actual rows and loops at relevant nodes alongside the table.

Include canonical and scratch size comparisons and individual index sizes in the report. The supplied query gives
complete table, all-index, total, and individual-index sizes in bytes; identify which metric you discuss.
Record both scratch row-count changes and the correctness checks for R1–R4. No separate metadata or check files are
required. The [optional report starter](../submission/report.md) helps organize this material.

Explain index use or non-use, composite column order, remaining aggregate/join/sort/window work, and how observations
compare with your original predictions. End with a counterexample, your retain/reject recommendation, a drawback,
and a changed-demand scenario that reverses a decision. Use your original workload priorities to weigh read,
INSERT, and storage effects. The assignment gives the complete requirements.

Timing includes EXPLAIN instrumentation; it is not end-to-end ingestion throughput or separate commit latency.
A read-only warm-up is not a cold-cache guarantee. Buffers count accesses, not unique disk reads, and parent counters
include child work, so do not sum them into a total. There is no required speedup or plan shape.

For example, a node estimating 100 rows but returning 4 rows with 3 loops returned about 12 rows across those loops.
Its buffer counters already cover its executions: do not multiply those counters by the loop count.
Use such observations to explain work, not as a substitute for checking the actual report results.
