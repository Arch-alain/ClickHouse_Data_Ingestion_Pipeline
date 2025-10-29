"""
clickhouse_utils.py
-------------------
Data cleaning and ClickHouse insertion utilities.
"""

import json
import time
import numpy as np
import pandas as pd
from datetime import datetime
from clickhouse_driver import Client


def clean_value(x):
    """Clean and standardize values before inserting into ClickHouse."""
    if isinstance(x, (int, float, str, bool, type(None), pd.Timestamp)):
        return None if pd.isnull(x) else x
    elif isinstance(x, (dict, list, np.ndarray)):
        return json.dumps(x, ensure_ascii=False)
    else:
        return str(x)


def gen_rows_for_insert(data: pd.DataFrame, timestamp_col: str = None):
    """Convert a DataFrame into ClickHouse-ready tuples."""
    col_names = [str(c) for c in data.columns]
    ts_index = data.columns.get_loc(timestamp_col) if timestamp_col else None
    rows = []

    for row in data.values.tolist():
        row = [clean_value(x) for x in row]

        if ts_index is not None and row[ts_index] is not None:
            val = row[ts_index]
            if isinstance(val, (pd.Timestamp, datetime)):
                row[ts_index] = val.strftime("%Y-%m-%d %H:%M:%S.%f")
            else:
                row[ts_index] = str(val)

        row = [int(x) if isinstance(x, bool) else x for x in row]
        rows.append(tuple(row))

    return col_names, rows


def push_data_in_chunks(
    client: Client,
    schema: str,
    table: str,
    data: pd.DataFrame,
    timestamp_col: str = None,
    chunk_size: int = 5000
):
    """
    Push a DataFrame to ClickHouse in chunks.

    Args:
        client: ClickHouse client instance.
        schema: Database name.
        table: Table name.
        data: Pandas DataFrame to insert.
        timestamp_col: Optional timestamp column.
        chunk_size: Number of rows per batch insert.
    """
    assert isinstance(data, pd.DataFrame), f"Expected DataFrame, got {type(data)}"
    data = data.dropna(axis=1, how='all')

    if data.empty:
        print("No data to insert.")
        return

    col_names, _ = gen_rows_for_insert(data.head(1), timestamp_col)
    col_str = "(" + ", ".join(col_names) + ")"
    total_rows = len(data)
    print(f"Total rows to insert: {total_rows}")

    start_total = time.time()
    for start_idx in range(0, total_rows, chunk_size):
        end_idx = min(start_idx + chunk_size, total_rows)
        chunk = data.iloc[start_idx:end_idx]
        _, rows = gen_rows_for_insert(chunk, timestamp_col)

        start = time.time()
        client.execute(
            f"INSERT INTO {schema}.{table} {col_str} VALUES",
            rows,
            types_check=True
        )
        print(f"Inserted rows {start_idx}-{end_idx-1} in {round(time.time() - start, 2)}s")

    print(f"✅ All data inserted in {round(time.time() - start_total, 2)}s")


def create_table_if_not_exists(client: Client, schema: str, table: str, columns_def: list):
    """
    Create ClickHouse table if it doesn't exist.

    Args:
        client: ClickHouse client instance.
        schema: Database/schema name.
        table: Table name.
        columns_def: List of column definitions as strings.
    """
    query = f"""
    CREATE TABLE IF NOT EXISTS {schema}.{table} (
        {', '.join(columns_def)}
    ) ENGINE = ReplacingMergeTree(timestamp)
    ORDER BY (parent_asin, timestamp)
    """
    client.execute(query)
