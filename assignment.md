# Assignment 2: Make It Fast—and Prove Why

This is an individual assignment worth **15 points**. It opens after Practice 8 / Week 4.
Practice 8 is a full window-functions workshop;
the next assignment studio is Practice 9. The assignment is designed to be completed independently on your own laptop.

After Practice 8, start setup and report correctness (R1–R4). Practice 9 supports the baseline investigation;
Practice 10 supplies the last required index and plan-reading preparation. Complete the index experiment and
recommendation after that preparation, using Practices 11–12 for evidence checks and explanation. You are not
expected to know all index concepts when the assignment first opens.

This brief contains all learner-facing requirements for Assignment 2. You do not need another assignment brief or a
document from the repository root to understand, complete, or submit it.

## Scenario

The campus mobility observatory records devices passing fixed stations. Write recent-device, daily-activity,
complete-dashboard, and network-ranking reports. Recommend a small index portfolio using observed read plans,
batch insertion, storage measurements, and your own causal explanations.

The data fixes report contents, but does not prescribe how often a real service runs them. Before predicting index
benefits, state a workload scenario in your report: relative demand for R1–R4, ingestion frequency using the
supplied batch size, and whether read latency, ingestion time, or storage is your main priority. Numbers may be
illustrative assumptions, not measured facts. Keep this scenario through your final recommendation; compare it with
one changed-demand scenario. There is no single best portfolio for every workload, and no extra benchmark is required.

Default has 1,000,000 initial events and 20,000 devices; reduced has 100,000 events and 2,000 devices. Both have 32
stations and 180 UTC dates in `[2026-01-01 00:00:00+00, 2026-06-30 00:00:00+00)`. Errors are rare but nonzero.
Record your chosen profile. Both profiles require every task, all five before/after comparisons, and the same
assessment, with equivalent opportunities for full credit. Intended eligible event population and SQL difficulty
increase from R1 to R4;
observed times and buffers need not increase. Full credit does not require a particular plan, scan node,
or minimum speedup.

## Learning Outcomes

By completing this assignment, you will be able to:

- verify report grain, time boundaries, missing dates, ties, and window frames;
- turn report and INSERT work into testable access-path hypotheses;
- compare PostgreSQL EXPLAIN plans before and after adding indexes, interpreting estimates, actual rows, loops,
  and buffers;
- compare index read benefits with insertion and storage consequences; and
- explain a counterexample and recommend indexes for a stated workload.

Plan approximately **8–12 hours** for setup, report writing, experiments, and analysis; your actual time may vary.
Confirm the profile and protocol in the first studio,
bring a paired plan comparison to the middle studio, and test the causal explanation in the final studio.

## Supplied Materials

Use the standalone `assignment-2-package/`: its README explains setup and connection, the experiment protocol
explains the before/after sequence, and the SQL guide and data dictionary support your investigation.
The package contains Docker setup, fixed data and parameters, a size query, and optional submission starters.
Use pgAdmin (included), DBeaver, or PyCharm to write and run your SQL. Docker handles setup and resets;
you do not need host Python or a custom runner, application, or database engine.

`mobility.stations` has `station_id` and `station_name`. One `mobility.events` row is an observation with `event_id`,
`device_id`, `station_id`, `event_time` (`timestamptz`), `event_type`, and `status` (`ok` or `error`). All columns are
non-null, event IDs are unique, device IDs are positive, and stations reference the 32 supplied stations (IDs 1–32).
`mobility.ingest_batch` supplies 10,000 new rows for default or 1,000 for reduced, with IDs exceeding historical IDs,
valid stations/devices, and times after the historical end. `a2_write.events` is a logged scratch copy for INSERT,
matching historical rows, types, constraints, and constraint indexes before each configuration's write.

A reset restores the same rows and fixed parameters for your chosen profile. Plans, timings, and physical sizes
may differ across machines or resets. Use UTC in every SQL session and date calculation. Insert the batch only
into the scratch table; keep `mobility.events` unchanged.

## Required Work

Complete all work yourself. Your submitted SQL, observations, and decisions must be your own, even if practice
activities involved discussion with peers.

You may discuss concepts, rehearse practice exercises, and compare interpretations of supplied evidence. Do not share
or copy submission files, finished queries, index definitions, hypotheses, findings, or captured assignment evidence.
You may reuse a course-designated shared starter, but you must adapt, verify, and explain it independently.
The course AI-use policy below applies unchanged, including its disclosure requirement.

### Operation Contract

All five operations below are compulsory. Each report is one student-written SELECT; CTEs remain part of that
statement. Use fixed parameters, never current dates or random devices. Keep SQL semantics identical between captures.

| Operation | Status | Output rows / inserted rows |
| --- | --- | --- |
| R1 | compulsory | 20 |
| R2 | compulsory | active dates |
| R3 | compulsory | 992 |
| R4 | compulsory | 5,760 |
| INSERT | compulsory | 10,000 / 1,000 |

### R1 Recent Device Observations

For device **42**, return its latest **20** historical observations: all six event columns ordered by
`event_time DESC, event_id DESC`. One row is one observation. Both profiles supply enough rows and a timestamp tie
relevant to winner ordering. Explain the predicate, LIMIT, and event-ID tie-breaker. Investigate whether an index can
retrieve this device's observations and provide useful ordering.

### R2 Station Daily Activity

For station **7** and `[2026-03-01 00:00:00+00, 2026-03-08 00:00:00+00)`, return `activity_date`,
`total_events`, and `error_events`, ordered by date ascending. Group by UTC date and compute errors with aggregate
FILTER or an equivalent justified conditional aggregate. Include only dates with activity. One row is an observed day
at that station. Count events, not distinct devices. Explain the inclusive start, exclusive end, and absence of the
deliberately quiet March 4. Both profiles supply start/end boundary cases and both statuses in the station/week.

### R3 Complete Network Dashboard

For all **32** stations and `[2026-03-01 00:00:00+00, 2026-04-01 00:00:00+00)`, return `station_id`,
`station_name`, `activity_date`, `total_events`, and `error_events`, ordered by date ascending then station ID
ascending. Return every station/date pair, with zero for missing counts: **992 rows**. One row is a calendar day
at a station, including quiet combinations. Use a complete station/date grid, event aggregation, and a left join.
The SQL guide illustrates a tiny Cartesian grid using unrelated values rather than a completed assignment report.

Explain why deriving stations/dates only from period events loses quiet combinations and why counts must not count
null-extended placeholder rows. Include March 4 and other quiet station/dates; check half-open boundaries.
R2's station/week counts must reconcile with corresponding R3 rows, treating omitted R2 dates as zero.

### R4 Network Rankings and Cumulative Activity

For all stations over `[2026-01-01 00:00:00+00, 2026-06-30 00:00:00+00)`, construct complete station/day
counts as in R3. Return R3's five columns plus `daily_rank` and `cumulative_events`, ordered by date ascending then
station ID ascending: **5,760 rows**. One row is a station/day with its daily network rank and cumulative activity.

Use DENSE_RANK partitioned by date, ordered by total count descending. Equal counts share dense rank; station ID
stabilizes display, not rank peers. Positive-count ties and the all-zero March 4 tie are supplied. Use running SUM per
station ordered by date with explicit `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` frame. Totals begin at the
historical boundary. Explain aggregation before windows and the two partitions/orderings. March counts must reconcile
with R3; each station's last cumulative value must equal its count over the full historical period. Ranking and running
totals are compulsory. LAG, moving averages, advanced indexes, and materialized reports are not hidden prerequisites.

### Hypotheses and Index Investigation

Use **one report** for your investigation, in Google Docs, Word, Markdown, PDF, or another readable format.
Before experiments, record a prediction for each of R1–R4 and INSERT: expected access/work, eligible-row share
where relevant, buffer or storage consequences, and your reason. Date this section and keep the original predictions;
add observations later. Confirmed and disproved predictions earn equal reasoning credit when explained.
The optional `submission/report.md` is a starter, not a required format.

`baseline` means the supplied constraints and automatic indexes, with no student-created indexes. `indexed` adds
**at most three additional index designs** on `mobility.events`; supplied primary-key and UNIQUE indexes do not
count. At least one design must be composite. Compare its column order using an exploratory alternative or precise
ordered-key reasoning tied to observed plans. A third index is not mandatory. For each final index, identify the
reports served, columns/order, expected benefit, measured size, and maintenance consequence. Remove rejected
exploratory indexes before the final comparison.

Keep your index SQL in labelled canonical (`mobility.events`) and scratch (`a2_write.events`) blocks. Scratch
indexes must match the canonical designs, including key order/direction, expressions, predicates, and included
columns if used. Scratch copies do not count as extra designs; scratch-only designs invalidate the write comparison.
Keep the final portfolio unchanged throughout indexed reads and INSERT. Preserve SQL, parameters, data, constraints,
and execution settings between configurations. Do not force planner choices, reorganize storage, or substitute
materialized results for the assessed indexing experiment.

### Before/After Experiment

Compare **all five operations** with and without your added indexes: four reports and one batch INSERT in each
configuration. This produces ten measured executions for the whole portfolio, not ten per index. Warm-ups,
correctness checks, and size queries are outside these measurements. Follow the package's experiment protocol:

1. Reset to the supplied historical data with primary keys and constraints intact and no student-created indexes.
   Record your profile and initial table/batch row counts. Run ANALYZE and record baseline table/index sizes.
2. Run R1–R4 once in order as a read warm-up. Then run each with `EXPLAIN (ANALYZE, BUFFERS)` and save a readable
   baseline plan. Inspect the actual report results separately to check correctness.
3. Count scratch rows as a read-only warm-up and record its sizes. Run your batch INSERT exactly once under
   `EXPLAIN (ANALYZE, BUFFERS)` with autocommit on. Save its plan, then record scratch row count and sizes again.
4. Rebuild scratch from the original historical rows using the supplied `reset-write` Docker command. Deleting the
   batch is not enough to restore comparable physical state.
5. Apply your final indexes to both canonical and scratch tables, then ANALYZE. Record indexed table/index sizes.
6. Repeat the same read warm-up, R1–R4 plan sequence, and report correctness checks with the final indexes.
7. Repeat the scratch count warm-up, before sizes, one measured INSERT, and after row count/sizes.
8. Compare both plans for every operation, the report results, and storage observations in your report.

Write one batch INSERT from `mobility.ingest_batch` into `a2_write.events`, with explicit target columns and fixed
source order (`event_id` ascending). Use the same statement in both configurations. Do not substitute COPY,
single-row loops, upserts, disabled constraints, or temporary/unlogged targets. No UPDATE experiment is required.
**EXPLAIN ANALYZE executes the INSERT.** With autocommit on it commits the batch; do not rerun it to obtain a result
count. Count scratch rows afterward instead. Setup, copying, index builds, and ANALYZE are outside measured INSERT
execution. Its instrumented timing does not measure end-to-end ingestion throughput or separate commit latency.

A read-only warm-up does not guarantee a cold cache. Never warm up by inserting into the measured target.
Every INSERT repeat needs a fresh scratch rebuild and the correct indexes. Label extra attempts and discuss
variation instead of selecting only the fastest run. Stop on SQL errors. If a write may have executed, reset scratch
before retrying; if the overall pair is no longer comparable, reset and start the pair again. Resets keep your work
files. You do not need to build reset infrastructure.

### Required Task: Compare EXPLAIN Plans and Recommend Indexes

For each of **R1, R2, R3, R4 and INSERT**, compare its baseline and indexed plans in your report. Include readable
plans in the report or clearly labelled attachments: copied text, optional JSON, or legible GUI screenshots are all
acceptable. Include enough detail to inspect the nodes and metrics you discuss; label the operation and configuration.

Include a **paired comparison table** covering all five operations. Five rows with before/after columns are recommended;
a ten-row table with one row per operation/configuration is also acceptable. Show execution time, relevant shared-buffer
hits/reads, and the main plan change. Use the explanation alongside each pair to cover:

1. Which added indexes the planner used, or why none was used; scan types, index conditions versus residual filters,
   and relevant sorting, joining, aggregation, or window work. For INSERT, explain index maintenance even when
   EXPLAIN has no separate node for each index update.
2. Estimated versus actual rows and loops at relevant nodes, observed time and buffers, what changed, and what work
   remained. Planner cost estimates are not milliseconds. Separate observations from your explanation and acknowledge
   measurement limits.
3. How the evidence relates to your original prediction: supported benefit, no benefit, regression, or inconclusive
   result. Explain unchanged plans and ignored indexes too; a timing difference alone is not a causal explanation.
4. What the result implies for your index choice, considering read benefits alongside measured INSERT and storage costs.

Include a **size comparison in the same report**: canonical table/index sizes before and after indexing, individual
index sizes, and scratch sizes before and after INSERT in both configurations. Use the supplied `sizes.sql` results
in bytes; keep complete table storage, aggregate index storage, and total storage distinct.

Explain correctness in the report as well. Inspect actual report results in both configurations for the required
values, row counts, duplicates, and order. Address the specified boundary, quiet-date, tie, and cross-report checks.
For each INSERT, show scratch count before and after, expected batch count, and the matching increase; explain why
your INSERT copies the supplied batch once and leaves the canonical report table unchanged. EXPLAIN rows alone do
not establish INSERT count or report correctness. Separate result exports are optional.

Finish with a counterexample and a recommendation. The counterexample must explain an available index that was
ignored or unjustified by workload benefit relative to insertion/storage costs. R4 is a possible broad-work candidate,
not a guaranteed answer. Name indexes to retain or reject, cite read/INSERT/size evidence, and identify a drawback.
Use the workload priorities recorded before experiments, then explain a changed-demand scenario that would reverse
one decision, such as more ingestion or different report demand. No extra benchmark or numerical break-even point is
required; a single instrumented run cannot establish a break-even point alone. Extra exploration must not change the
report contracts or add a fourth final index.

Buffers describe accesses, not unique physical reads; do not sum inclusive parent and child counters as total work.
There is no required scan type, percentage speedup, or laptop ranking. Neither slower indexed INSERTs nor larger
measured growth is a pass condition: allocation, caching, and overhead can obscure differences. Explain maintenance
and storage consequences without inventing per-index costs from portfolio totals. Copied plans, unexplained metrics,
and unsupported claims that more indexes are always better are insufficient.

## AI Tools Usage Policy

This policy covers generative AI tools, including chatbots, code generators, and other AI-driven tools. It applies to
all course activities. It supplements the current KSE academic-integrity requirements; where a university rule and
this policy differ, the current KSE rule applies.

### Allowed Uses

Students may use AI tools for:

- brainstorming ideas and approaches;
- preparing for tests or the final exam, for example by generating practice questions or requesting explanations of
  concepts;
- editing the language and structure of student-written documentation without generating its assessed technical
  reasoning, decisions, evidence, or conclusions; and
- syntax and reference questions during practical sessions and practical assignments, for example asking how to
  create an index in PostgreSQL, how to interpret a SQL construct, or how to call a stored procedure.

### Prohibited Uses

Students must not use AI tools to:

- complete a graded assignment, practical task, test, or exam in place of their own work;
- include the full assignment conditions in a prompt or ask for a complete solution;
- submit AI-generated SQL queries, database schemas, analyses, explanations, or code as their own work; or
- use AI tools in an assessment when the assessment instructions do not permit them.

### Conditions for Use

When a submission includes AI-generated content, students must clearly identify the content and provide the original
prompt or prompts used to generate it. Students remain responsible for checking the accuracy of any AI-generated
material and for being able to explain the submitted work. AI-generated content without clear disclosure is treated
as unauthorized use.

For practical assignments, disclosure is made in `AI_DISCLOSURE.md` and names the tool, date, original prompt,
affected files or passages, and how the student checked and revised the output. Asking for a syntax example, an error
explanation, or feedback on a student-written fragment can be allowed. Asking for a complete schema, query set,
analysis, decision record, or assignment is prohibited. Language editing does not permit replacement of the student's
technical reasoning with generated reasoning.

### Non-Compliance

Work completed by AI without the required disclosure will not be evaluated. Unauthorized AI use may result in a
formal warning, a grade reduction, or other consequences under the current KSE academic-integrity requirements.

## Required Submission

Submit your SQL, one investigation report, and readable before/after plans for all five operations. A convenient
arrangement is `workload.sql` (labelled R1–R4), `indexes.sql` (canonical and scratch blocks), `insert.sql`, and your
report, with plan attachments only if they are not embedded. Other clear arrangements are acceptable; there is no
required directory tree or report file format. The package starters are optional.

Your report must contain the original workload assumptions and hypotheses, five paired plan comparisons and their
measurement table, correctness and INSERT row-count checks, a size comparison, causal explanations, a counterexample,
and your final recommendation. State the selected profile and clearly reference any attachments. The submitted SQL
and the supplied protocol
should be sufficient to repeat the investigation; explain any deviations that affect your measurements. You do not
need separate metadata, size, check, or
result-export files.

Submit one ZIP archive to the Moodle activity named in the course announcement. For a Google Docs report, export a
PDF so the submitted report is stable and readable. Check that the archive includes all SQL and plan evidence and opens
correctly. Include only your submission materials, without database data, containers, runtime files, or local passwords.
Moodle's recorded submission time is authoritative. A replacement uploaded before the applicable cutoff supersedes
the earlier archive. Ordinary replacement closes after the cutoff unless an approved institutional exception applies.
The course announcement states the archive-size limit, support route, and feedback location.

When your submission includes AI-generated content, also include `AI_DISCLOSURE.md` with the tool, date, original
prompts, affected files/passages, and your checking/revision account, as required by the AI policy above.
Disclosure does not make prohibited assistance permissible.

## Assessment

This individual assignment is worth **15 points**: **technical correctness — 6 points** and
**assignment defence — 9 points**.

- **Technical correctness — 6 points**
  - Repeatable workload — 1 point: all four reports and batch INSERT are labelled, semantically correct, executable,
    and repeatable; result checks cover required grain and boundaries.
  - Index designs and investigation — 3 points: at most three supported designs, a composite-order comparison,
    explicit R1–R4 baseline/indexed EXPLAIN analysis, removed exploratory indexes, and causal explanations.
  - Counterexample — 1 point: an ignored or unjustified index explained using actual workload and cost evidence.
  - Read/INSERT/storage tradeoff — 1 point: correct paired INSERT plan analysis and size evidence, supported
    recommendation, drawback, and workload-change condition.
- **Assignment defence — 9 points**
  - Two questions from the published bank of ten — 4 points: 2 points per question, comprising 1 point for technical
    accuracy and 1 point for an explanation with a relevant example or application.
  - Additional TA questions about your submitted work — 5 points:
    - Solution understanding — 2 points: Explain report/INSERT SQL and indexes, including a rejected or ignored index.
    - Evidence interpretation — 2 points: Interpret paired plans, actual results, comparable state, and sizes.
    - Trade-offs and changes — 1 point: Justify a read/write/storage decision or predict changed workload effects.
- **Total — 15 points**

Required evidence, verification output, documentation, and reproducible execution support the technical assessment;
they do not carry separate points. Plan files or timing tables without analysis do not satisfy the comparison task.
Technical correctness is assessed from the submitted work, while defence points
assess your own answers during the practical session. A correct written explanation does not replace an oral answer.
Apply dependency-aware marking without repeated deductions for one root cause. Index quantity, prescribed plans,
optional mastery, and particular laptop timing earn no automatic reward.

### Defence Procedure

Defend the assignment individually in front of a TA during a scheduled practical session. The TA selects two distinct
questions from the ten below and asks additional questions about your submitted code, data model, decisions, and
evidence. Prepare all ten questions and be ready to navigate and explain your submitted work.

You may consult your submitted files when discussing the work, but must answer independently without live assistance.
Marks assess technical understanding rather than presentation polish. The TA records the two selected question
numbers and the reasons for the awarded points. There is no separate pass threshold for either part of the defence.

A submission awaiting its scheduled defence has a provisional technical score. Course staff publish defence slots,
permitted materials, and missed-defence/make-up arrangements before assessment, in accordance with current university
requirements. After those arrangements are exhausted, unanswered defence components earn zero. A staff-scheduled
defence after the submission deadline does not make an on-time submission late. The existing late-submission cap
applies to the total technical-correctness and defence score.

### Defence Question Bank

1. How do pages, locality, and the buffer pool affect the cost of reading a table?
2. Why can a sequential scan be preferable to an index scan for a broad report?
3. What is selectivity, and how does changing reporting scope affect access-path choices?
4. How does column order affect a composite index for predicates and requested ordering?
5. Why can a report return few rows while processing many observations, and which aggregation,
   joining, or window work can remain after indexing?
6. What workload change could make a useful index less valuable, and what maintenance cost remains?
7. How do estimated rows, actual rows, loops, and buffer observations help explain a plan?
8. What must remain comparable between baseline and indexed runs, including the INSERT reset?
9. What does paired batch INSERT and size evidence show about portfolio costs, and what does it not establish?
10. How do report grain, quiet dates, time boundaries, ranking ties, and window frames affect correctness?
    Illustrate with one submitted report and predict a small changed condition.

## Deadlines

The assignment opens after Practice 8 / Week 4. Full credit is
available until the published timestamp immediately before **Practice 14 / Week 7**, at least seven calendar days
after Practice 12. The late-submission period ends seven calendar days later
in **Week 8** and has a maximum possible mark of **7.5 points** out of 15, regardless of raw rubric score. Work
submitted after the late cutoff earns zero unless an approved institutional exception applies.

Check the course announcement for the exact Europe/Kyiv submission timestamps and defence slots.
The late cutoff is seven calendar days after the full-credit deadline.

## Optional Extension

Covering/index-only and partial indexes may be investigated after required basic/composite work. Explain
their conditions and costs if used; they cannot replace the required composite comparison and are not
needed for full base credit. Optional exploration does not automatically earn additional points.
WAL measurement is optional; logging/recovery internals are not required knowledge here.

After completing all required work, you may add a clearly marked, non-assessed note in your report proposing one
additional workload change and predicting how it would alter the final recommendation. Do not add a fourth final
index or change R1–R4 or the batch INSERT for this extension.
