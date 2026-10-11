# Data dictionary

[Fixed parameters](../data/parameters.json) accompany the bundled data.
The historical period is `[2026-01-01 00:00:00+00, 2026-06-30 00:00:00+00)`: 180 UTC dates, with the end excluded.
Reset restores the same logical rows, IDs, timestamps, batch, and parameters for the selected profile.
Physical files, plans, timings, and sizes may differ across machines or resets.

| Profile | Historical events | Device IDs | Stations | New batch rows |
| --- | ---: | --- | ---: | ---: |
| default | 1,000,000 | 1–20,000 | 32 | 10,000 |
| reduced | 100,000 | 1–2,000 | 32 | 1,000 |

Both profiles have the same tasks and marking. Device scaling preserves the meaningful device-42 top-20 lookup.
The quiet date March 4, other quiet station/date pairs, boundary events, rare errors, and positive-count ties
are deliberate. Event counts describe observations, not distinct devices or registration-state changes.

<!-- rumdl-disable MD013 -->

| Relation | Grain and columns | Rules |
| --- | --- | --- |
| `mobility.stations` | One station: `station_id integer`, `station_name text` | NOT NULL; primary key; IDs 1–32 |
| `mobility.events` | One historical observation: `event_id bigint`, `device_id integer`, `station_id integer`, `event_time timestamptz`, `event_type text`, `status text` | Six NOT NULL columns; event primary key; positive device; station FK; status `ok`/`error` |
| `mobility.ingest_batch` | One new observation; same six columns | Same constraints; unique IDs above historical maximum; existing stations/devices; timestamps after historical end |
| `a2_write.events` | Logged experimental copy of historical observations | Same six-column types, constraints and automatic indexes; rebuilt in event-ID order before each write configuration |

<!-- rumdl-enable MD013 -->

Only scratch receives the batch. Keep canonical `mobility.events` unchanged. Supplied constraint indexes remain
in the baseline and do not count against your three additional designs.

R1 uses device 42's latest 20 observations, ordered by timestamp then ID descending. R2 uses station 7's active
dates from March 1–8. R3 covers all stations from March 1–April 1, including zeros, for 992 station/dates.
R4 covers the entire historical period for 5,760 station/dates, with daily dense rank and per-station running total.
See [the brief](../assignment.md) for exact columns/order and [the protocol](experiment-protocol.md) for the comparison.
