import redis
import requests
import json
import logging
from datetime import datetime

from helper_modules.saving_state import RedisStorage
from helper_modules.utils import init_coroutine, backoff

logger = logging.getLogger('app_logger')


class ESLoader:
    """Класс загрузки данных в Elasticsearch"""

    def __init__(self, dsn: dict):
        self.dsn_es = dsn
        self.url = f'http://{self.dsn_es.get("host")}:{self.dsn_es.get("port")}/_bulk'
        self.redis = redis.Redis
        self.state = RedisStorage(self.redis)
        self.name_key = 'current_offset'
        self.index_name = 'movies'

    @backoff(exception_class=requests.exceptions.RequestException)
    @init_coroutine
    def load_data_coroutine(self, datetime_update_key: str, limit: int):
        """
        :param datetime_update_key: ключ из redis для последнего время обновления записей в таблице (нужен для
        обновления времени)
        :param limit: лимит записей которые будем брать
        :return: None
        """

        try:
            while True:
                movies = yield
                while movies:
                    movies_list = []
                    for movie in movies[:limit]:
                        movies_list.extend([
                            json.dumps({'index': {'_index': self.index_name, '_id': movie.get('id')}}),
                            json.dumps(movie)
                        ])

                    movies = movies[limit:]
                    self.send_data_to_elastic(movies_list)

                    if movies_list:
                        self.state.save_state(datetime_update_key, str(datetime.now()))
        except GeneratorExit:
            logger.info(msg='uploaded the records to elasticsearch')

    @backoff(exception_class=requests.exceptions.RequestException)
    def send_data_to_elastic(self, prepare_data):
        """
        Метод для отправки данных пачками в elasticsearch
        :param prepare_data: пачка данных для загрузки в elasticsearch
        :return:
        """

        str_query = '\n'.join(prepare_data) + '\n'
        response = requests.post(
            self.url,
            data=str_query,
            headers={'Content-Type': 'application/x-ndjson'}
        )

        json_response = json.loads(response.content.decode())
        for item in json_response['items']:
            error_message = item['index'].get('error')
            if error_message:
                logger.error(msg=error_message)

