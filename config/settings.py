import yaml
from dataclasses import dataclass, field
from typing import Dict, Optional
from urllib.parse import parse_qs


@dataclass
class ApiConfig:
    base_url: str
    params: Dict[str, str] = field(default_factory=dict)
    pause_sec: float = 1.0
    timeout: int = 30
    retries: int = 2
    limit: int = 100

    @classmethod
    def from_dict(cls, api_dict: dict) -> "ApiConfig":
        base_url = api_dict["base_url"]
        query_str = api_dict.get("params", {}).get("query_string", "")
        params = parse_qs(query_str)
        limit = int(params.pop("limit", [100])[0])
        flat_params = {k: v[0] for k, v in params.items()}
        request_cfg = api_dict.get("request", {})
        return cls(
            base_url=base_url,
            params=flat_params,
            pause_sec=request_cfg.get("pause_sec", 1),
            timeout=api_dict.get("timeout", 30),
            retries=api_dict.get("retries", 2),
            limit=min(limit, 100)
        )


@dataclass
class StorageConfig:
    db_dir: str = "data"
    log_references: bool = False

    @classmethod
    def from_dict(cls, storage_dict: dict) -> "StorageConfig":
        return cls(
            db_dir=storage_dict.get("db_dir", "data"),
            log_references=storage_dict.get("log_references", False)
        )


@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: Optional[str] = None

    @classmethod
    def from_dict(cls, log_dict: dict) -> "LoggingConfig":
        return cls(
            level=log_dict.get("level", "INFO"),
            file=log_dict.get("file")
        )


@dataclass
class AppConfig:
    api: ApiConfig
    storage: StorageConfig
    logging: LoggingConfig

    @classmethod
    def from_yaml(cls, path: str = "config.yaml") -> "AppConfig":
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(
            api=ApiConfig.from_dict(data.get("source_api", {})),
            storage=StorageConfig.from_dict(data.get("storage", {})),
            logging=LoggingConfig.from_dict(data.get("logging", {}))
        )
