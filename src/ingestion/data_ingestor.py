"""
data_ingestor.py
----------------
Main script to handle data ingestion:
- Downloading files from URL
- Unzipping compressed files
- Processing JSON/JSONL datasets
- Loading data into ClickHouse
"""

import os
import logging
import argparse
import numpy as np
import pandas as pd
from clickhouse_driver import Client

from src.utils.file_utils import *
from src.utils.ingestion_utils import *
from src.utils.clickhouse_utils import *
from src.configs.config import (
    CLICKHOUSE_HOST, CLICKHOUSE_USER, CLICKHOUSE_PASSWORD, CLICKHOUSE_DB,
    DATA_DIR, DATA_DIR_ZIPPED, LOGS_DIR, PROCESSED_LOG, PROCESSED_LOG_ZIPPED
)

# ------------------- Ensure directories exist -------------------
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DATA_DIR_ZIPPED, exist_ok=True)

# ------------------- Logging Setup -------------------
LOG_FILE = os.path.join(LOGS_DIR, "data_ingestion.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)


# ------------------- Helper Functions -------------------
def download_mode(url: str):
    logging.info(f"Downloading file from URL: {url}")
    downloaded_file = download_file(url, DATA_DIR_ZIPPED)
    logging.info(f"Downloaded file: {downloaded_file}")
    return downloaded_file


def unzipping_mode():
    logging.info("=== Unzipping new files ===")
    processed_hashes = load_processed_files(PROCESSED_LOG_ZIPPED)
    new_files = get_new_zipped_files(DATA_DIR_ZIPPED, processed_hashes)

    if not new_files:
        logging.info("No new zipped files to unzip.")
        return

    for file_path, file_hash in new_files:
        extracted_files = decompress_file(file_path, DATA_DIR)
        logging.info(f"Unzipped {file_path} → {extracted_files}")
        processed_hashes.append(file_hash)
        save_processed_files(processed_hashes, PROCESSED_LOG_ZIPPED)


def process_mode():
    logging.info("=== Processing unzipped files ===")
    df = process_files(DATA_DIR, PROCESSED_LOG)
    if df.empty:
        logging.info("No new files to process.")
        return

    # Convert complex columns to JSON
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].apply(lambda x: isinstance(x, (dict, list))).any():
            df[col] = df[col].apply(convert_to_json)

    # Determine ClickHouse table schema
    columns_def = []
    for col in df.columns:
        sample_value = df[col].dropna().iloc[0] if not df[col].dropna().empty else ""
        ch_type = map_dtype(col, sample_value)
        columns_def.append(f"{col} {ch_type}")

    # Connect to ClickHouse
    client = Client(
        host=CLICKHOUSE_HOST,
        port=9000,
        user=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
        database=CLICKHOUSE_DB
    )

    # Create table if it doesn't exist
    create_table_if_not_exists(client, 'analytics_db', 'fashion_reviews', columns_def)

    # Insert data in chunks
    chunks = np.array_split(df, 20)
    for idx, chunk in enumerate(chunks):
        push_data_in_chunks(client, 'analytics_db', 'fashion_reviews', chunk, 'timestamp')
        logging.info(f"Inserted chunk {idx+1} of 20 | shape: {chunk.shape}")


# ------------------- Main Function -------------------
def main():
    logging.info("=== Data Ingestion Process Started ===")

    # Parse CLI arguments
    parser = argparse.ArgumentParser(description="Data ingestion pipeline for JSON/JSONL datasets")
    parser.add_argument("--url", type=str, help="URL to download data from")
    parser.add_argument("--unzipping", action="store_true", help="Process already downloaded zip files")
    parser.add_argument("--process", action="store_true", help="Process unzipped files and load into ClickHouse")
    args = parser.parse_args()

    try:
        if args.url:
            download_mode(args.url)

        if args.unzipping:
            unzipping_mode()

        if args.process:
            process_mode()

    except Exception as e:
        logging.error(f"❌ Data ingestion failed: {e}", exc_info=True)
        raise

    logging.info("=== Data Ingestion Process Finished ===")


# ------------------- Entry Point -------------------
if __name__ == "__main__":
    main()
