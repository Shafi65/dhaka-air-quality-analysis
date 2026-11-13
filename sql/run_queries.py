"""Run every query in sql/queries.sql against the DuckDB database and print the results.

Run sql/etl.py first to build sql/air_quality.db.
"""
import os
import sys

import duckdb

HERE = os.path.dirname(__file__)
DB_PATH = os.path.join(HERE, "air_quality.db")
QUERIES_PATH = os.path.join(HERE, "queries.sql")


def split_queries(text):
    """Split the file on ';' and pair each query with the comment line above it."""
    for block in text.split(";"):
        lines = [l for l in block.strip().splitlines() if l.strip()]
        sql = "\n".join(l for l in lines if not l.lstrip().startswith("--"))
        if not sql.strip():
            continue
        comments = [l.lstrip("- ").strip() for l in lines if l.lstrip().startswith("--")]
        yield (comments[-1] if comments else "query"), sql


def main():
    if not os.path.exists(DB_PATH):
        sys.exit(f"{DB_PATH} not found. Run sql/etl.py first.")
    con = duckdb.connect(DB_PATH, read_only=True)
    with open(QUERIES_PATH) as f:
        for title, sql in split_queries(f.read()):
            print(f"\n== {title}")
            print(con.sql(sql))
    con.close()


if __name__ == "__main__":
    main()
