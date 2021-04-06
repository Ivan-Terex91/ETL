from typing import Any
import redis

from settings import dsn_red
from .utils import backoff


class RedisStorage:
    """Класс для сохранения и считывания состояния в redis"""

    def __init__(self, redis_conn):
        self.redis_adapter = redis_conn(**dsn_red)

    @backoff(exception_class=redis.ConnectionError)
    def save_state(self, key: str, state: Any) -> None:
        self.redis_adapter.set(key, state)

    @backoff(exception_class=redis.ConnectionError)
    def retrieve_state(self, key: str) -> str:
        raw_data = self.redis_adapter.get(key)
        return raw_data.decode('utf-8') if raw_data else 0
