import os
from dotenv import load_dotenv

load_dotenv()

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "default")
DATA_DIR = os.getenv("DATA_DIR", "data/raw_unzipped")
DATA_DIR_ZIPPED = os.getenv("DATA_DIR_ZIPPED", "data/raw_zipped")
LOGS_DIR = os.getenv("LOGS_DIR", "logs")
PROCESSED_LOG = os.getenv("PROCESSED_LOG", "data/processed/processed_log.json")
PROCESSED_LOG_ZIPPED = os.getenv("PROCESSED_ZIPPED_LOG", "data/processed/processed_zipped_log.json")
