import sqlite3
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class SyncStorage:
    def __init__(self, db_dir: str = "data", log_references: bool = False):
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.db_path = self.db_dir / f"sync_{self.timestamp}.db"
        self.conn = sqlite3.connect(str(self.db_path))
        self.log_references = log_references
        self._init_schema()

    def _init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                reference TEXT PRIMARY KEY,
                updated_at TEXT,
                created_at TEXT,
                raw_json TEXT NOT NULL,
                fetched_at TEXT NOT NULL
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sync_meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        self.conn.commit()

    def save_batch(self, items: List[dict], fetched_at: str):
        with self.conn:
            for item in items:
                ref = item.get("reference")
                if not ref:
                    logger.warning("Skipping item without reference")
                    continue
                self.conn.execute("""
                    INSERT OR REPLACE INTO properties (reference, updated_at, created_at, raw_json, fetched_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    ref,
                    item.get("updatedAt"),
                    item.get("createdAt"),
                    json.dumps(item, ensure_ascii=False),
                    fetched_at
                ))
        logger.debug(f"Saved {len(items)} items to {self.db_path}")

    def write_reference_log(self, references: List[str]):
        if not references:
            return
        log_path = self.db_dir / f"sync_{self.timestamp}_refs.txt"
        with open(log_path, "w", encoding="utf-8") as f:
            for ref in references:
                f.write(ref + "\n")
        logger.info(f"Reference log written to {log_path}")

    def close(self):
        self.conn.close()
        logger.info(f"Database connection closed: {self.db_path}")
