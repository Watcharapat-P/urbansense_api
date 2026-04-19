"""
seed_db.py — Load all four MySQL dumps into the SQLite database.

Usage:
    python seed_db.py \
        --sound       path/to/urbansense_s.sql \
        --temp-humid  path/to/urbansense_t_h.sql \
        --weather     path/to/weather_stations.sql \
        --mrt         path/to/mrt_ridership.sql
"""

import argparse
import re
import sqlite3
from pathlib import Path

DB_PATH = "urbansense.db"


def read_inserts(sql_path: str) -> list[tuple[str, str]]:
    """Return list of (table_name, values_clause) from INSERT statements."""
    text = Path(sql_path).read_text(encoding="utf-8")
    # Match: INSERT INTO `table` (...) VALUES (...)
    pattern = re.compile(
        r"INSERT INTO `(\w+)`\s*\([^)]+\)\s*VALUES\s*(.*?);",
        re.DOTALL | re.IGNORECASE,
    )
    return pattern.findall(text)


def extract_column_names(sql_path: str, table: str) -> list[str]:
    text = Path(sql_path).read_text(encoding="utf-8")
    pattern = re.compile(
        r"INSERT INTO `" + table + r"`\s*\(([^)]+)\)\s*VALUES",
        re.IGNORECASE,
    )
    m = pattern.search(text)
    if not m:
        return []
    cols = [c.strip().strip("`") for c in m.group(1).split(",")]
    return cols


def load_file(conn: sqlite3.Connection, sql_path: str):
    inserts = read_inserts(sql_path)
    cur = conn.cursor()
    for table, values_block in inserts:
        cols = extract_column_names(sql_path, table)
        col_str = ", ".join(cols)
        placeholders = ", ".join(["?"] * len(cols))

        # Split individual row tuples
        row_pattern = re.compile(r"\(([^()]*)\)", re.DOTALL)
        rows = row_pattern.findall(values_block)

        for row in rows:
            # Parse values (handles quoted strings and numbers)
            values = []
            for val in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", row):
                val = val.strip()
                if val.upper() == "NULL":
                    values.append(None)
                elif val.startswith("'") and val.endswith("'"):
                    values.append(val[1:-1])
                else:
                    try:
                        values.append(int(val))
                    except ValueError:
                        try:
                            values.append(float(val))
                        except ValueError:
                            values.append(val)

            try:
                cur.execute(
                    f"INSERT OR IGNORE INTO {table} ({col_str}) VALUES ({placeholders})",
                    values,
                )
            except sqlite3.Error as e:
                print(f"  Warning [{table}]: {e} — row skipped")

    conn.commit()
    print(f"  ✓ Loaded {sql_path}")


def main():
    parser = argparse.ArgumentParser(description="Seed urbansense.db from SQL dumps")
    parser.add_argument("--sound", required=True, help="urbansense_s.sql path")
    parser.add_argument("--temp-humid", required=True, dest="temp_humid", help="urbansense_t_h.sql path")
    parser.add_argument("--weather", required=True, help="weather_stations.sql path")
    parser.add_argument("--mrt", required=True, help="mrt_ridership.sql path")
    args = parser.parse_args()

    # Create tables via SQLAlchemy first
    from app.database import engine
    from app import models
    models.Base.metadata.create_all(bind=engine)
    print("Tables created.")

    conn = sqlite3.connect(DB_PATH)
    for path in [args.sound, args.temp_humid, args.weather, args.mrt]:
        load_file(conn, path)
    conn.close()
    print("Done! Database seeded.")


if __name__ == "__main__":
    main()
