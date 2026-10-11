# My Assignment 2 investigation

This is an optional report starter. Replace prompts with your own account, or use another document format.
Keep the hypotheses written before experiments when you add your findings.

## Setup and workload assumptions

Selected profile (default or reduced):

My workload scenario: relative demand for R1–R4, ingestion frequency at the supplied batch size, and the main
priority (read latency, ingestion time, or storage). Label illustrative numbers as assumptions.

## Hypotheses — complete before experiments

For each operation, predict access/work, eligible-row share where relevant, buffers or storage consequences,
and the reason. Keep the original prediction even if the evidence later disproves it.

| Operation | Prediction and reason |
| --- | --- |
| R1 | |
| R2 | |
| R3 | |
| R4 | |
| INSERT | |

Proposed indexes and reports served; expected benefits; composite-column-order prediction:

## Correctness

Explain the report grain, requested ordering, and checks of actual results in both configurations:

- R1: latest 20, device filter, timestamp ties and event-ID ordering.
- R2: half-open week, active dates only, errors, quiet March 4.
- R3: 992 station/dates, zeros, boundaries, and reconciliation with R2.
- R4: 5,760 station/dates, March reconciliation with R3, dense-rank peers, and final cumulative totals.

How did I check that adding indexes preserved values, row counts, duplicates, and order?

| Configuration | Scratch rows before | Scratch rows after | Increase | Expected batch rows | Canonical rows after |
| --- | --- | --- | --- | --- | --- |
| baseline | | | | | |
| indexed | | | | | |

Explain why my INSERT copies the batch once with its values preserved, and how scratch was rebuilt before the
indexed write. Identify any failed/repeated attempts and how comparable state was restored.

## Paired plan comparisons

Include the ten readable plans here or refer to clearly labelled attachments. Text, optional JSON, and legible
GUI screenshots are acceptable. Complete this five-row paired table, or use ten rows with one per
operation/configuration. Buffer entries should identify relevant shared hits/reads and the node or scope.

| Operation | Baseline time (ms) | Indexed time (ms) | Baseline buffers | Indexed buffers | Main plan change |
| --- | --- | --- | --- | --- | --- |
| R1 | | | | | |
| R2 | | | | | |
| R3 | | | | | |
| R4 | | | | | |
| INSERT | | | | | |

For each pair, refer to both plans and explain index use or non-use, work changed and remaining, relevant
estimated/actual rows and loops, and what the observations mean for the original hypothesis and index choice.
Distinguish measurements from proposed explanations. For INSERT, account for index maintenance even if it has
no separate plan node. A timing difference alone is not an explanation.

### R1

### R2

### R3

### R4

### INSERT

## Storage and composite order

Copy sizes from the supplied `sizes.sql` into this report. Include canonical sizes in both configurations and
scratch sizes before and after INSERT. Keep complete table, aggregate index, and total storage distinct.

| Relation / phase | Baseline table bytes | Indexed table bytes | Baseline index bytes | Indexed index bytes |
| --- | --- | --- | --- | --- |
| Canonical before writes | | | | |
| Scratch before INSERT | | | | |
| Scratch after INSERT | | | | |

Record total storage and each individual index's size in an additional table or alongside these observations.
Explain the measured storage consequences and their limits.

How did composite column order affect predicates and ordering? Explain an exploratory alternative or precise
ordered-key reasoning using the observed plans. Which work remained after indexing?

## Counterexample and recommendation

Explain an available index ignored by the planner or unjustified by workload benefit relative to INSERT/storage
costs. Which indexes would I retain or reject, and why? Cite read plans, INSERT, and sizes together, state a
drawback, and connect the decision to the workload priorities recorded before experiments.

What changed report demand or ingestion priority would reverse one decision? Explain why; no extra benchmark is
required. What can my timing, buffer, and storage observations not establish?

If required by the course policy, include a separate `AI_DISCLOSURE.md` with the original prompts and other
required disclosure details.
