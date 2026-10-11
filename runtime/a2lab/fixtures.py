"""Transactional setup for the supplied data and the INSERT experiment.

Resets replace only marked Assignment 2 tables, preserve unrelated objects and
roll back on failure. Loading and ANALYZE are setup work, not measurements.
"""

import csv
from dataclasses import dataclass
import gzip
from pathlib import Path

import psycopg
from psycopg import Connection, sql

from .contract import Profile, STATION_COUNT, profile_spec

ASSIGNMENT = "assignment-2-postgresql"
SQL_ROOT = Path(__file__).resolve().parents[1] / "sql"
RELATIONS = ("mobility.stations", "mobility.events", "mobility.ingest_batch", "a2_write.events", "a2_meta.fixture")
DROP_ORDER = ("a2_write.events", "mobility.ingest_batch", "mobility.events", "mobility.stations", "a2_meta.fixture")
EVENT_COLUMNS = ("event_id", "device_id", "station_id", "event_time", "event_type", "status")


@dataclass(frozen=True)
class FixtureState:
    profile: Profile
    canonical_rows: int
    scratch_rows: int
    batch_rows: int


def _database_guard(conn: Connection) -> None:
    if conn.execute("SELECT current_database()").fetchone()[0] != "assignment2":
        raise ValueError("fixture database must be assignment2; no assignment DDL was attempted")


def _transaction_settings(conn: Connection) -> None:
    conn.execute("SET LOCAL timezone = 'UTC'")
    conn.execute("SET LOCAL search_path = pg_catalog")
    conn.execute("SELECT pg_advisory_xact_lock(20261007, 2)")


def _namespace_guard(conn: Connection) -> bool:
    schemas = conn.execute("SELECT nspname FROM pg_namespace WHERE nspname = ANY(%s)",
                           (["mobility", "a2_write", "a2_meta"],)).fetchall()
    if not schemas:
        return False
    marker = conn.execute("SELECT c.relkind, c.relpersistence FROM pg_class c JOIN pg_namespace n "
                          "ON n.oid=c.relnamespace WHERE n.nspname='a2_meta' AND c.relname='fixture'").fetchone()
    if marker != ("r", "p"):
        raise ValueError("unmarked assignment schema; refusing to replace existing work")
    try:
        rows = conn.execute("SELECT assignment, profile "
                            "FROM a2_meta.fixture WHERE singleton IS TRUE").fetchall()
        count = conn.execute("SELECT count(*) FROM a2_meta.fixture").fetchone()[0]
    except psycopg.Error as exc:
        raise ValueError("assignment ownership marker is invalid") from exc
    if (count != 1 or len(rows) != 1 or rows[0][0] != ASSIGNMENT
            or rows[0][1] not in ("default", "reduced")):
        raise ValueError("assignment ownership marker does not match Assignment 2")
    objects = conn.execute("""SELECT n.nspname, c.relname, c.relkind, pn.nspname, p.relname
        FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        LEFT JOIN pg_index i ON i.indexrelid=c.oid LEFT JOIN pg_class p ON p.oid=i.indrelid
        LEFT JOIN pg_namespace pn ON pn.oid=p.relnamespace
        WHERE n.nspname = ANY(%s)""", (["mobility", "a2_write", "a2_meta"],)).fetchall()
    for namespace, name, kind, parent_namespace, parent in objects:
        own_table = f"{namespace}.{name}" in RELATIONS and kind == "r"
        own_index = kind == "i" and f"{parent_namespace}.{parent}" in RELATIONS
        if not (own_table or own_index):
            raise ValueError(f"unexpected object in assignment namespace: {namespace}.{name}; reset refused")
    attached = conn.execute("""SELECT n.nspname, c.relname, t.tgname FROM pg_trigger t
        JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname=ANY(%s) AND NOT t.tgisinternal
        UNION ALL SELECT n.nspname, c.relname, r.rulename FROM pg_rewrite r
        JOIN pg_class c ON c.oid=r.ev_class JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname=ANY(%s)""",
        (["mobility", "a2_write", "a2_meta"], ["mobility", "a2_write", "a2_meta"])).fetchall()
    if attached:
        raise ValueError(f"unexpected trigger/rule in assignment namespace: {'.'.join(attached[0])}; reset refused")
    policies = conn.execute("""SELECT n.nspname, c.relname, p.polname FROM pg_policy p
        JOIN pg_class c ON c.oid=p.polrelid JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname=ANY(%s)""", (["mobility", "a2_write", "a2_meta"],)).fetchall()
    if policies:
        raise ValueError(f"unexpected policy in assignment namespace: {'.'.join(policies[0])}; reset refused")
    extras = conn.execute("""SELECT n.nspname, p.proname FROM pg_proc p
        JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname=ANY(%s)
        UNION ALL SELECT n.nspname, t.typname FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace
        WHERE n.nspname=ANY(%s) AND t.typrelid=0 AND NOT EXISTS
          (SELECT 1 FROM pg_type base WHERE base.typarray=t.oid AND base.typrelid<>0)
        UNION ALL SELECT n.nspname, pg_describe_object(d.classid,d.objid,d.objsubid)
        FROM pg_depend d JOIN pg_namespace n ON n.oid=d.refobjid
        WHERE d.refclassid='pg_namespace'::regclass AND n.nspname=ANY(%s)
        AND d.classid NOT IN ('pg_class'::regclass,'pg_type'::regclass,'pg_proc'::regclass)""",
        (["mobility", "a2_write", "a2_meta"], ["mobility", "a2_write", "a2_meta"],
         ["mobility", "a2_write", "a2_meta"])).fetchall()
    if extras:
        raise ValueError(f"unexpected object in assignment namespace: {extras[0][0]}.{extras[0][1]}; reset refused")
    return True


def _grants(conn: Connection, relations: tuple[str, ...]) -> list[tuple[str, str, str, bool]]:
    return conn.execute("""SELECT n.nspname||'.'||c.relname, r.rolname, a.privilege_type, a.is_grantable
        FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        CROSS JOIN LATERAL aclexplode(c.relacl) a JOIN pg_roles r ON r.oid=a.grantee
        WHERE n.nspname||'.'||c.relname=ANY(%s) AND a.grantee<>c.relowner""", (list(relations),)).fetchall()


def _regrant(conn: Connection, grants: list[tuple[str, str, str, bool]]) -> None:
    for relation, role, privilege, grantable in grants:
        # privilege comes from aclexplode, never caller SQL.
        conn.execute(sql.SQL("GRANT {} ON TABLE {} TO {}{}").format(sql.SQL(privilege),
            sql.Identifier(*relation.split(".")), sql.Identifier(role),
            sql.SQL(" WITH GRANT OPTION" if grantable else "")))


def _copy_data(conn: Connection, data_root: Path, profile: Profile, relation: str, filename: str) -> None:
    path = Path(data_root) / profile / filename
    opener = gzip.open if filename.endswith(".gz") else open
    query = sql.SQL("COPY {} FROM STDIN WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8')").format(
        sql.Identifier(*relation.split(".")))
    with opener(path, "rb") as source:
        header = source.readline()
        expected = ("station_id", "station_name") if filename == "stations.csv" else EVENT_COLUMNS
        if tuple(next(csv.reader([header.decode("utf-8")]))) != expected:
            raise ValueError(f"unexpected columns in {profile}/{filename}")
        with conn.cursor() as cur, cur.copy(query) as copy:
            copy.write(header)
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                copy.write(chunk)


def _loaded_state(conn: Connection, profile: Profile) -> FixtureState:
    spec = profile_spec(profile)
    counts = tuple(conn.execute(sql.SQL("SELECT count(*) FROM {}").format(
        sql.Identifier(*relation.split(".")))).fetchone()[0] for relation in RELATIONS[:4])
    if counts != (STATION_COUNT, spec.event_count, spec.batch_count, spec.event_count):
        raise ValueError("loaded row counts do not match the selected profile; reset rolled back")
    return FixtureState(profile, counts[1], counts[3], counts[2])


def reset_fixture(conn: Connection, data_root: Path, profile: Profile, *, allow_profile_change: bool = False) -> FixtureState:
    profile_spec(profile)
    _database_guard(conn)
    try:
        with conn.transaction():
            _transaction_settings(conn)
            installed = _namespace_guard(conn)
            if installed:
                old_profile = conn.execute("SELECT profile FROM a2_meta.fixture").fetchone()[0]
                if old_profile != profile and not allow_profile_change:
                    raise ValueError("profile mismatch; use --allow-profile-change to switch profiles")
            grants = _grants(conn, RELATIONS) if installed else []
            for relation in DROP_ORDER:
                conn.execute(sql.SQL("DROP TABLE IF EXISTS {} RESTRICT").format(sql.Identifier(*relation.split("."))))
            conn.execute((SQL_ROOT / "schema.sql").read_text(encoding="utf-8"))
            for relation, filename in (("mobility.stations", "stations.csv"), ("mobility.events", "events.csv.gz"),
                                       ("mobility.ingest_batch", "ingest_batch.csv")):
                _copy_data(conn, data_root, profile, relation, filename)
            _copy_data(conn, data_root, profile, "a2_write.events", "events.csv.gz")
            conn.execute("INSERT INTO a2_meta.fixture VALUES (true, %s, %s)", (ASSIGNMENT, profile))
            _regrant(conn, grants)
            for relation in RELATIONS[:4]:
                conn.execute(sql.SQL("ANALYZE {}").format(sql.Identifier(*relation.split("."))))
            return _loaded_state(conn, profile)
    except psycopg.errors.DependentObjectsStillExist as exc:
        raise ValueError("external dependency prevents reset; previous tables and dependent objects preserved") from exc
    except psycopg.Error as exc:
        raise ValueError("data/schema load failed; reset transaction rolled back") from exc


def reset_write(conn: Connection, data_root: Path, profile: Profile) -> FixtureState:
    profile_spec(profile)
    _database_guard(conn)
    try:
        with conn.transaction():
            _transaction_settings(conn)
            if not _namespace_guard(conn):
                raise ValueError("assignment data is absent; run reset first")
            if conn.execute("SELECT profile FROM a2_meta.fixture").fetchone()[0] != profile:
                raise ValueError("profile mismatch; use the profile selected during setup")
            grants = _grants(conn, ("a2_write.events",))
            conn.execute("DROP TABLE a2_write.events RESTRICT")
            conn.execute("""CREATE TABLE a2_write.events (
                event_id bigint PRIMARY KEY,
                device_id integer NOT NULL CHECK (device_id > 0),
                station_id integer NOT NULL REFERENCES mobility.stations (station_id),
                event_time timestamptz NOT NULL,
                event_type text NOT NULL,
                status text NOT NULL CHECK (status IN ('ok', 'error'))
            )""")
            _copy_data(conn, data_root, profile, "a2_write.events", "events.csv.gz")
            _regrant(conn, grants)
            conn.execute("ANALYZE a2_write.events")
            return _loaded_state(conn, profile)
    except psycopg.errors.DependentObjectsStillExist as exc:
        raise ValueError("external dependency prevents INSERT-table reset; previous state preserved") from exc
    except psycopg.Error as exc:
        raise ValueError("INSERT-table rebuild failed; reset transaction rolled back") from exc
