import time
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from requests.exceptions import Timeout, ConnectionError
import logging
from typing import Iterator
from src.domain.models import ApiResponse

logger = logging.getLogger(__name__)


class LextrusApiClient:
    def __init__(self, base_url: str, params: dict, limit: int,
                 timeout: int = 30, pause_sec: float = 1.0, retries: int = 2):
        self.base_url = base_url.rstrip("/")
        self.params = params
        self.limit = limit
        self.timeout = timeout
        self.pause_sec = pause_sec
        self.retries = retries
        self.session = requests.Session()

    def _build_params(self, offset: int) -> dict:
        return {**self.params, "limit": self.limit, "offset": offset}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((Timeout, ConnectionError)),
        reraise=True
    )
    def _request_with_retry(self, offset: int) -> requests.Response:
        url = self.base_url
        params = self._build_params(offset)
        logger.debug(f"GET {url} with params={params}")
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response

    def fetch_page(self, offset: int) -> ApiResponse:
        try:
            resp = self._request_with_retry(offset)
            data = resp.json()
            return ApiResponse(**data)
        except Exception as e:
            logger.error(f"Failed to fetch page offset={offset}: {e}")
            raise

    def fetch_all(self) -> Iterator[ApiResponse]:
        first_page = self.fetch_page(0)
        yield first_page
        total = first_page.total
        logger.info(f"Total objects reported by API: {total}")

        for offset in range(self.limit, total, self.limit):
            time.sleep(self.pause_sec)
            try:
                page = self.fetch_page(offset)
                yield page
            except Exception:
                logger.exception(f"Failed to fetch offset {offset}, stopping pagination")
                break
