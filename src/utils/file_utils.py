"""
file_utils.py
-------------
File download, decompression, JSON/JSONL loading, and processed file tracking utilities.
"""

import os
import gzip
import zipfile
import json
import logging
import requests
import hashlib
import pandas as pd
import polars as pl


# ------------------- File Download & Decompression -------------------
def download_file(url: str, dest_folder: str) -> str:
    """Download a file from a URL and save it locally."""
    os.makedirs(dest_folder, exist_ok=True)
    local_filename = os.path.join(dest_folder, os.path.basename(url))
    logging.info(f"Downloading dataset from {url}")

    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    logging.info(f"File downloaded: {local_filename}")
    return local_filename


def decompress_file(file_path: str, output_folder: str) -> list:
    """Decompress .gz or .zip files and return extracted file paths."""
    os.makedirs(output_folder, exist_ok=True)
    extracted_paths = []

    if file_path.endswith(".gz"):
        filename = os.path.basename(file_path).replace(".gz", "")
        output_path = os.path.join(output_folder, filename)
        with gzip.open(file_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            f_out.write(f_in.read())
        extracted_paths.append(output_path)

    elif file_path.endswith(".zip"):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if not member.endswith('/'):
                    output_path = os.path.join(output_folder, os.path.basename(member))
                    with zip_ref.open(member) as source, open(output_path, 'wb') as target:
                        target.write(source.read())
                    extracted_paths.append(output_path)

    else:
        # If not compressed, just copy the file
        output_path = os.path.join(output_folder, os.path.basename(file_path))
        with open(file_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            f_out.write(f_in.read())
        extracted_paths.append(output_path)

    logging.info(f"Extracted: {extracted_paths}")
    return extracted_paths


# ------------------- JSON / JSONL Loading -------------------
def load_json_or_jsonl(file_path: str) -> pl.DataFrame:
    """Load JSON or JSONL file into a Polars DataFrame."""
    logging.info(f"Loading file into Polars: {file_path}")
    if file_path.endswith(".jsonl"):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = [json.loads(line) for line in f]
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    return pl.DataFrame(data)


def load_json_or_jsonl_pandas(file_path: str) -> pd.DataFrame:
    """Load JSON or JSONL file into a Pandas DataFrame."""
    logging.info(f"Loading file into Pandas: {file_path}")
    if file_path.endswith(".jsonl"):
        return pd.read_json(file_path, lines=True)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            return pd.DataFrame(json.load(f))


# ------------------- Processed File Tracking -------------------
def load_processed_files(processed_log: str) -> list:
    """Load previously processed file hashes from a JSON log."""
    if not os.path.exists(processed_log):
        logging.info("Processed log not found.")
        return []

    try:
        with open(processed_log, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, ValueError):
        logging.warning("Processed log is empty or corrupted.")
        return []


def save_processed_files(new_files: list, processed_log: str):
    """Append new processed file hashes to the log."""
    processed = load_processed_files(processed_log)
    updated = list(set(processed + new_files))
    with open(processed_log, 'w') as f:
        json.dump(updated, f, indent=2)


def compute_file_hash(file_path: str) -> str:
    """Compute MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_new_zipped_files(folder: str, processed_hashes: list) -> list:
    """Return list of new .gz or .zip files that have not been processed."""
    all_files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.endswith(".gz") or f.endswith(".zip")
    ]

    new_files = []
    for file in all_files:
        file_hash = compute_file_hash(file)
        if file_hash not in processed_hashes:
            new_files.append((file, file_hash))

    return new_files
