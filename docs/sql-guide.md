# SQL guidance and checks

[The assignment](../assignment.md) gives each required grain, columns, ordering, and fixed UTC parameters.
Write each report as one SELECT, optionally using CTEs. Use inclusive starts and exclusive ends with literal UTC
bounds. Aggregate observations, complete the station/date grid, then apply windows where required.

## An unrelated two-by-three grid

This example combines two colours with three sizes into six pairs. Adapt the concept yourself to the required
station/date grain.

```sql
WITH colours(colour) AS (VALUES ('blue'), ('gold')),
     sizes(size) AS (VALUES ('small'), ('medium'), ('large'))
SELECT colour, size
FROM colours CROSS JOIN sizes
ORDER BY colour, size;
```

An event-derived list loses absent dates or stations. A LEFT JOIN preserves the complete grid, but `count(*)`
counts null-extended placeholder rows too. Decide which non-null matched key or preaggregated count your query
needs and explain zero completion. Keep UTC date conversion consistent with the fixed bounds.

Dense-rank peers are defined by daily event totals; the display tie-breaker is not an extra rank key.
Use separate daily-network and station-history partitions/orderings, and an explicit running-SUM ROWS frame.

## Simple row-count checks

Run these in your SQL client outside measured executions:

```sql
SET timezone = 'UTC';
SELECT count(*) AS historical_rows FROM mobility.events;
SELECT count(*) AS batch_rows FROM mobility.ingest_batch;
SELECT count(*) AS scratch_rows FROM a2_write.events;
```

Before each measured INSERT, scratch count must equal historical count. Afterward it must increase by the batch
count: 10,000 for default or 1,000 for reduced. Record both configurations' before/after counts in your report.
Keep the canonical historical count unchanged. Counts help detect mistakes; explain how your INSERT selects the
supplied batch once with all six columns and preserves values. An INSERT plan's output rows alone do not establish
how many rows were added.

Write one INSERT with explicit target columns and source `event_id` order. Use the supplied Docker `reset-write`
command before the indexed write or any repeat; see [the protocol](experiment-protocol.md). Rebuilding scratch
restores the logged historical table, constraints, and original row order. Do not substitute DELETE, disable
constraints, or change the target to an unlogged table.

## Record sizes

Open [sizes.sql](../runtime/sql/sizes.sql) in your client. Run its queries and copy the relevant values into the
report: canonical sizes before/after indexing, each individual index, and scratch sizes before/after INSERT in
both configurations. In pgAdmin, select and execute each complete SELECT separately to inspect each result.

The first query reports complete table, aggregate index, and total storage for both tables in bytes. The second
reports individual index sizes. Keep these metrics distinct; total storage includes table and indexes. Include the
supplied primary key when describing overall index storage, and identify your added indexes individually.

## Inspect plans and correctness

Use `EXPLAIN (ANALYZE, BUFFERS)` before your SELECT or INSERT to get execution time, row observations, and buffers.
It executes the statement, so run each measured INSERT only once. JSON is optional; add `FORMAT JSON` if you prefer.
Keep a readable full plan or legible screenshots for each operation/configuration.

Predict access, selectivity, ordering, and remaining aggregate/window work before observing plans. At most three
additional designs may remain in the final portfolio. Include a composite-order investigation using an alternative
or precise ordered-key reasoning tied to the plans. Scratch definitions must mirror the canonical portfolio.

Plans do not show the report's returned values. Run the SELECTs separately and check the following in both states:

- R1: 20 observations for device 42, correct newest-first order and event-ID tie-breaker.
- R2: station 7's active dates in the half-open week, errors counted correctly, and quiet March 4 omitted.
- R3: 992 station/dates with zeros, correct boundaries, and R2 station/week counts reconciled with omitted dates
  as zero.
- R4: 5,760 station/dates, March counts matching R3, correct dense-rank peers including March 4, and each station's
  final cumulative value matching its historical event count.

Compare actual baseline/indexed values, row counts, duplicates, and requested order. Describe how you checked them
in your report; exports are optional. Matching results do not prove the SQL is correct, so also explain the grain,
boundaries, quiet dates, ties, and window frame. The report should connect these checks to your SQL choices.
