 # 🧩 Data Ingestion Pipeline for ClickHouse

This project automates the process of **downloading, extracting, processing, and loading large-scale JSON/JSONL datasets** into a **ClickHouse** database.

It is designed as a **modular and reusable pipeline** for data engineers who want to manage ingestion workflows efficiently while preventing duplicate processing.

---

## 🚀 Overview

The pipeline is built to handle the entire lifecycle of ingesting large, compressed datasets. It performs the following key tasks:

* **Download** compressed files from a given URL.
* **Decompress** `.gz` or `.zip` files automatically into a staging area.
* **Track processed files** using hash-based logs to **avoid re-ingestion** (deduplication).
* **Process and clean** JSON/JSONL data into **Pandas DataFrames**.
* **Insert cleaned data into ClickHouse in batches** for efficient, high-performance ingestion.

---

## 🏗️ Project Structure

The project uses a clear, modular structure for easy maintenance and extension:

## 🧠 Key Components

### 1. `file_utils.py`
Handles all I/O operations outside of the database:
* File download from URL (`download_file`).
* Decompression of `.gz` and `.zip` files (`decompress_file`).
* Loading JSON/JSONL files into Pandas or Polars DataFrames.

### 2. `ingestion_utils.py`
Manages the deduplication and process tracking logic:
* File **hash computation** for unique identification.
* Tracking processed files in simple JSON logs.
* Filtering out already processed files based on the logs.

### 3. `clickhouse_utils.py`
Manages the final step of data preparation and loading:
* Data cleaning and type conversion (e.g., handling nested JSON).
* Conversion of nested data structures to flat JSON strings if necessary.
* **Batch insertion** into ClickHouse for optimal performance.

### 4. `data_ingestor.py`
The main orchestrator:
* It ties together all utilities to execute the download, unzip, process, and upload workflow.
* Uses **CLI arguments** for flexible execution of each step.

## 🧩 Usage

Run the script from the project root using the Python module execution:

```bash
# Example: Download, unzip, and process a file in one command
python -m src.ingestion.data_ingestor --url "[https://example.com/data.json.gz](https://example.com/data.json.gz)" --unzipping --process

Available OptionsArgumentDescription--urlURL of the dataset to download. Triggers the download step.--unzippingUnzips any new compressed files in the data_zipped directory.--processProcesses new unzipped files in the data directory and loads them into ClickHouse.

Example Workflow
You can run each step independently, which is useful for large datasets or scheduled jobs:

1. Download new compressed file(s)
Bash

python -m src.ingestion.data_ingestor --url "[https://example.com/data.gz](https://example.com/data.gz)"
2. Unzip new compressed files
This step checks processed_log_zipped.json to only unzip newly downloaded files.

Bash

python -m src.ingestion.data_ingestor --unzipping
3. Process and push to ClickHouse
This step checks processed_log.json to only process files not yet inserted into ClickHouse.

Bash

python -m src.ingestion.data_ingestor --process
🧾 Logging
All pipeline activities are logged to logs/data_ingestion.log. This includes:

Download and extraction progress.

Files processed or skipped (due to deduplication).

ClickHouse insertion status and batch metrics.

🧰 Dependencies
Install all necessary dependencies using the provided requirements.txt file:

Bash

pip install -r requirements.txt
Example primary dependencies include:

pandas / polars (for data processing)

clickhouse-driver (for database connection)

requests (for file downloading)

python-dotenv (for configuration management)