from config.settings import AppConfig
from src.infrastructure.api_client import LextrusApiClient
from src.infrastructure.storage import SyncStorage
from src.application.usecases.fetch_and_store import FetchAndStoreUseCase
from logger_config import setup_logging

def main():
    config = AppConfig.from_yaml("config.yaml")
    setup_logging({"level": config.logging.level, "file": config.logging.file})

    api_client = LextrusApiClient(
        base_url=config.api.base_url,
        params=config.api.params,
        limit=config.api.limit,
        timeout=config.api.timeout,
        pause_sec=config.api.pause_sec,
        retries=config.api.retries
    )
    storage = SyncStorage(
        db_dir=config.storage.db_dir,
        log_references=config.storage.log_references
    )
    usecase = FetchAndStoreUseCase(api_client=api_client, storage=storage)
    usecase.execute()

if __name__ == "__main__":
    main()
