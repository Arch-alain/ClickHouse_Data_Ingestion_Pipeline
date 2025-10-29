# 🧩 Data Ingestion Pipeline for ClickHouse

This project automates the process of downloading, extracting, processing, and loading large-scale Amazon product review datasets (JSON/JSONL format) into a ClickHouse database.

It is designed as a modular and reusable pipeline to enable efficienncy in managing Amazon review data ingestion workflows while preventing duplicate processing.


---

## 🚀 Overview

The pipeline performs the following tasks:

- **Download** compressed files from a given URL
- **Decompress** `.gz` or `.zip` files automatically
- **Track** processed files to avoid re-ingestion
- **Process** and clean JSON/JSONL data into Pandas DataFrames
- **Insert** cleaned data into ClickHouse in batches for efficient ingestion

---

## 🏗️ Project Structure

```
project_root/
├── src/
│   ├── configs/
│   │   └── config.py               # Environment variables & directories
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── data_ingestor.py        # Main entry point
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_utils.py           # File handling & decompression
│   │   ├── ingestion_utils.py      # Process tracking & deduplication
│   │   └── clickhouse_utils.py     # ClickHouse cleaning & batch insertion
│
├── logs/                           # Log files from ingestion runs
├── data/                           # Unzipped datasets
├── data_zipped/                    # Raw downloaded compressed files
├── processed_log.json              # Tracks processed unzipped files
├── processed_log_zipped.json       # Tracks processed zipped files
└── README.md
```

---

## ⚙️ Configuration

### Environment Variables Setup

Create a `.env` file in the project root (this file should be added to `.gitignore`):

```bash
# ClickHouse Connection Settings
CLICKHOUSE_HOST=localhost
CLICKHOUSE_USER=analytics
CLICKHOUSE_PASSWORD=your_secure_password_here
CLICKHOUSE_DB=amazon_reviews_db

# Directory Configuration
DATA_DIR=data
DATA_DIR_ZIPPED=data_zipped
LOGS_DIR=logs

# Process Tracking Files
PROCESSED_LOG=processed_log.json
PROCESSED_LOG_ZIPPED=processed_log_zipped.json
```

---

## 🧠 Key Components

### 1. `file_utils.py`
Handles:
- File download from URL (`download_file`)
- Decompression of `.gz` and `.zip` files (`decompress_file`)
- Loading JSON/JSONL files into Pandas or Polars

### 2. `ingestion_utils.py`
Handles:
- File hash computation for deduplication
- Tracking processed files in JSON logs
- Filtering out already processed files

### 3. `clickhouse_utils.py`
Handles:
- Data cleaning and type conversion
- Batch insertion into ClickHouse
- Conversion of nested data structures to JSON

### 4. `data_ingestor.py`
Orchestrates the entire ingestion flow:
- Downloads, unzips, processes, and uploads data
- Uses CLI arguments for flexibility

---

## 🧩 Usage

Run the script from the project root:

```bash
python -m src.ingestion.data_ingestor --url "https://example.com/data.json.gz"
```

### Available Options

| `--url` | URL of the dataset to download |

| `--unzipping` | Unzips any new compressed files |

| `--process` | Processes unzipped files and loads them into ClickHouse |


## 🗃️ Example Workflow

### 1. Download new file
```bash
python -m src.ingestion.data_ingestor --url "https://example.com/data.gz"
```

### 2. Unzip new compressed files
```bash
python -m src.ingestion.data_ingestor --unzipping
```

### 3. Process and push to ClickHouse
```bash
python -m src.ingestion.data_ingestor --process
```

---

## 🧾 Logging

All logs are stored in `logs/data_ingestion.log` and include:

- Download and extraction progress
- Files processed or skipped
- ClickHouse insertion status

---

## 🧰 Dependencies

Install dependencies with:

```bash
pip install -r requirements.txt
```

### Example dependencies:

```
pandas
numpy
polars
clickhouse-driver
requests
python-dotenv
```

---