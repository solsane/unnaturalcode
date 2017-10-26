#!/usr/bin/env python3

import sqlite3
from pathlib import Path

aggregate_db = Path('results-aggregate.sqlite3')

COLUMNS = """
id,mutation,good_file,bad_file,iteration,tool,change_operation,good_token_type,good_token_value,bad_token_type,bad_token_value,change_token_index,change_start_line,change_start_col,change_end_line,change_end_col,line_location_rank,line_location_index,line_location_start_line,line_location_start_col,line_location_end_line,line_location_end_col,line_location_token_type,line_location_token_value,line_location_operation,window_location_rank,window_location_index,window_location_start_line,window_location_start_col,window_location_end_line,window_location_end_col,window_location_token_type,window_location_token_value,window_location_operation,exact_location_rank,exact_location_index,exact_location_start_line,exact_location_start_col,exact_location_end_line,exact_location_end_col,exact_location_token_type,exact_location_token_value,exact_location_operation,valid_fix_rank,valid_fix_index,valid_fix_start_line,valid_fix_start_col,valid_fix_end_line,valid_fix_end_col,valid_fix_token_type,valid_fix_token_value,valid_fix_operation,true_fix_rank,true_fix_index,true_fix_start_line,true_fix_start_col,true_fix_end_line,true_fix_end_col,true_fix_token_type,true_fix_token_value,true_fix_operation
"""

COLUMNS_NEAT = COLUMNS.strip().replace('id', 'id PRIMARY KEY', 1).replace(',', ',\n  ')

SCHEMA = f"""
CREATE TABLE results (
  {COLUMNS_NEAT},
  partition
);
"""


def database_paths():
    for path in Path('.').glob('results.*'):
        if not path.is_dir():
            print("skipping", path)
            continue
        db_path =  path / 'results.sqlite3'
        if not db_path.exists():
            print("WARNING:", db_path, "does not exist!")
        try:
            partition = int(path.suffix.lstrip('.'))
        except ValueError:
            print("Could not figure out partition:", path)
            exit(-1)
        yield partition, db_path


if aggregate_db.exists():
    print("Deleting previous aggregate database")
    aggregate_db.unlink()

conn = sqlite3.connect(str(aggregate_db))
conn.executescript(SCHEMA)

for partition, db_path in database_paths():
    print("attaching to", db_path)
    conn.execute("""
        ATTACH DATABASE ? AS other
    """, (str(db_path.absolute()),))

    count, = conn.execute("SELECT COUNT(*) FROM other.results").fetchone()
            
    # Copy everything over from the other database.
    print(" * Copying", count, "results")
    with conn:
        conn.execute(f"""
            INSERT INTO results ({COLUMNS}, partition)
            SELECT {COLUMNS}, ? FROM other.results
        """, (partition,))

    conn.execute("""
        DETACH DATABASE other
    """)
