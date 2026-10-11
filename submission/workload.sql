-- Write one SELECT, optionally with CTEs, for each labelled report.
-- Keep SQL and fixed parameters identical in baseline and indexed runs.
-- Run R1-R4 once as warm-up, then EXPLAIN (ANALYZE, BUFFERS) for each.
-- Inspect actual results separately for correctness; save readable plans.

-- R1: Device 42; latest 20; all six columns;
-- event_time DESC, event_id DESC.
-- Your SELECT here.

-- R2: Station 7; UTC [2026-03-01, 2026-03-08); active dates only.
-- activity_date, total_events, error_events; date ascending.
-- Your SELECT here.

-- R3: All 32 stations; UTC [2026-03-01, 2026-04-01); full grid with zeros.
-- station_id, station_name, activity_date, total_events, error_events.
-- 992 rows; date then station ID ascending.
-- Your SELECT here.

-- R4: All stations; UTC [2026-01-01, 2026-06-30); complete counts then windows.
-- R3 columns plus daily_rank and cumulative_events; 5760 rows.
-- Dense-rank peers by daily total; explicit per-station running ROWS frame.
-- Date then station ID ascending.
-- Your SELECT here.
