import logging
from datetime import datetime, timezone
from src.infrastructure.api_client import LextrusApiClient
from src.infrastructure.storage import SyncStorage

logger = logging.getLogger(__name__)


class FetchAndStoreUseCase:
    def __init__(self, api_client: LextrusApiClient, storage: SyncStorage):
        self.api_client = api_client
        self.storage = storage

    def execute(self):
        fetched_at = datetime.now(timezone.utc).isoformat()
        total_saved = 0
        all_refs = []

        try:
            for page in self.api_client.fetch_all():
                if not page.data:
                    continue
                items_dicts = [item.dict() for item in page.data]
                self.storage.save_batch(items_dicts, fetched_at)

                refs = [item.reference for item in page.data if item.reference]
                all_refs.extend(refs)
                total_saved += len(items_dicts)
                logger.info(f"Saved {len(items_dicts)} items (total so far: {total_saved})")

            if self.storage.log_references and all_refs:
                self.storage.write_reference_log(all_refs)

            with self.storage.conn:
                self.storage.conn.execute(
                    "INSERT OR REPLACE INTO sync_meta (key, value) VALUES (?, ?)",
                    ("total_saved", str(total_saved))
                )
                self.storage.conn.execute(
                    "INSERT OR REPLACE INTO sync_meta (key, value) VALUES (?, ?)",
                    ("fetched_at", fetched_at)
                )
            logger.info(f"Sync completed. Total objects saved: {total_saved}")

        except Exception as e:
            logger.exception("Fatal error during fetch and store execution")
            raise
        finally:
            self.storage.close()
