"""Load the supplied data or reset the INSERT table."""

import argparse
from collections.abc import Sequence
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assignment 2 database setup")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (("reset", "load the supplied data and remove student indexes"),
                            ("reset-write", "restore the INSERT table and remove its student indexes")):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--profile", choices=("default", "reduced"))
        if name == "reset":
            command.add_argument("--allow-profile-change", action="store_true")
    args = parser.parse_args(argv)
    if args.profile is None:
        print(f"{args.command}: --profile default|reduced is required", file=sys.stderr)
        return 2
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print(f"{args.command}: DATABASE_URL is required inside the tools container", file=sys.stderr)
        return 1
    import psycopg
    from .fixtures import reset_fixture, reset_write

    try:
        with psycopg.connect(database_url, autocommit=True, connect_timeout=5,
                             options="-c timezone=UTC") as conn:
            data_root = Path(os.environ.get("A2_DATA_ROOT", "/data"))
            if args.command == "reset":
                state = reset_fixture(conn, data_root, args.profile,
                                      allow_profile_change=args.allow_profile_change)
            else:
                state = reset_write(conn, data_root, args.profile)
        print(json.dumps(asdict(state)))
    except (ValueError, OSError) as exc:
        print(f"{args.command}: {exc}", file=sys.stderr)
        return 1
    except psycopg.Error:
        # Driver errors can contain connection credentials.
        print(f"{args.command}: database connection failed; check the db service", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
