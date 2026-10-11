-- Setup work only: run inside the supplied guarded reset transaction.
-- These five exact relations are the Assignment 2 lifecycle's ownership boundary.
CREATE SCHEMA IF NOT EXISTS mobility;
CREATE SCHEMA IF NOT EXISTS a2_write;
CREATE SCHEMA IF NOT EXISTS a2_meta;

CREATE TABLE mobility.stations (
    station_id integer PRIMARY KEY,
    station_name text NOT NULL
);
CREATE TABLE mobility.events (
    event_id bigint PRIMARY KEY,
    device_id integer NOT NULL CHECK (device_id > 0),
    station_id integer NOT NULL REFERENCES mobility.stations (station_id),
    event_time timestamptz NOT NULL,
    event_type text NOT NULL,
    status text NOT NULL CHECK (status IN ('ok', 'error'))
);
CREATE TABLE mobility.ingest_batch (
    event_id bigint PRIMARY KEY,
    device_id integer NOT NULL CHECK (device_id > 0),
    station_id integer NOT NULL REFERENCES mobility.stations (station_id),
    event_time timestamptz NOT NULL,
    event_type text NOT NULL,
    status text NOT NULL CHECK (status IN ('ok', 'error'))
);
CREATE TABLE a2_write.events (
    event_id bigint PRIMARY KEY,
    device_id integer NOT NULL CHECK (device_id > 0),
    station_id integer NOT NULL REFERENCES mobility.stations (station_id),
    event_time timestamptz NOT NULL,
    event_type text NOT NULL,
    status text NOT NULL CHECK (status IN ('ok', 'error'))
);
-- Internal ownership marker used only by the reset commands.
CREATE TABLE a2_meta.fixture (
    singleton boolean PRIMARY KEY CHECK (singleton),
    assignment text NOT NULL,
    profile text NOT NULL CHECK (profile IN ('default', 'reduced'))
);
