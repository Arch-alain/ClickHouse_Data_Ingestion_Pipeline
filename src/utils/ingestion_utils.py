"""
ingestion_utils.py
------------------
Manage processed file tracking, de-duplication, and JSON/JSONL file ingestion.
"""

import os
import json
import hashlib
import pandas as pd
from .file_utils import *
import numpy as np


def load_processed_files(processed_log: str) -> list:
    """Load previously processed file hashes from a JSON log."""
    if not os.path.exists(processed_log):
        return []

    try:
        with open(processed_log, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, ValueError):
        return []


def save_processed_files(new_files: list, processed_log: str):
    """Append new file hashes to the processed log."""
    processed = load_processed_files(processed_log)
    updated = list(set(processed + new_files))
    with open(processed_log, "w") as f:
        json.dump(updated, f, indent=2)


def get_new_files(data_folder: str, processed_hashes: list) -> list:
    """
    Return a list of new `.jsonl` files that have not been processed yet.

    Returns:
        List of tuples: (file_path, file_hash)
    """
    all_files = [
        os.path.join(data_folder, f)
        for f in os.listdir(data_folder)
        if f.endswith(".jsonl")
    ]
    new_files = []
    for file in all_files:
        file_hash = compute_file_hash(file)
        if file_hash not in processed_hashes:
            new_files.append((file, file_hash))
    return new_files


def get_new_zipped_files(folder: str, processed_hashes: list) -> list:
    """Return new `.gz` files not yet processed."""
    all_files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.endswith(".gz")
    ]
    return [(file, compute_file_hash(file)) for file in all_files if compute_file_hash(file) not in processed_hashes]


def process_files(data_folder: str, processed_log: str) -> pd.DataFrame:
    """
    Process new JSONL files and return a concatenated Pandas DataFrame.

    Args:
        data_folder: Folder containing JSONL files.
        processed_log: Path to processed file hash log.

    Returns:
        Pandas DataFrame with all new files concatenated.
    """
    processed_hashes = load_processed_files(processed_log)
    new_files = get_new_files(data_folder, processed_hashes)

    if not new_files:
        print("No new files found.")
        return pd.DataFrame()

    all_dfs = []
    for file_path, file_hash in new_files:
        try:
            df = load_json_or_jsonl_pandas(file_path)
            all_dfs.append(df)
            processed_hashes.append(file_hash)
        except Exception as e:
            print(f"❌ Failed to process {file_path}: {e}")

    save_processed_files(processed_hashes, processed_log)
    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()


def convert_to_json(x):
    """Convert Python dict/list to JSON string."""
    return None if x is None else json.dumps(x)


def map_dtype(col_name, sample_value):
    """Map Python/Pandas dtypes to ClickHouse column types."""

    if isinstance(sample_value, (int, np.integer)):
        return "Int32"
    elif isinstance(sample_value, (float, np.floating)):
        return "Float32"
    elif isinstance(sample_value, (bool, np.bool_)):
        return "UInt8"
    elif isinstance(sample_value, (dict, list)):
        return "String"
    else:
        return "String"
