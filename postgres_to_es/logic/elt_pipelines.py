import redis
from datetime import datetime, timedelta
import logging

from extract_data_from_postgres import PostgresLoader
from helper_modules.saving_state import RedisStorage
from transform_data import transform_movies_coroutine
from load_to_elastic import ESLoader
from helper_modules.utils import backoff

logger = logging.getLogger('app_logger')


class ETLPipelines:
    """
    Класс формирующий пайплайны.
    Принимает все необходимые параметры для формирования etl процессов в виде пайплайнов.
    """

    def __init__(self, etl_process_name: str, extract: PostgresLoader, transform: transform_movies_coroutine,
                 load: ESLoader):
        """

        :param etl_process_name: имя ETL процесса
        :param extract: экземпляр класса для выгрузки данных из БД
        :param transform: трансформатор данных
        :param load: экземпляр класса для загрузки данных из Elasticsearch
        """
        self.extract = extract
        self.transform = transform
        self.load = load
        self.redis = redis.Redis
        self.state = RedisStorage(self.redis)
        self.etl_process_name = etl_process_name
        self.datetime_update_key = ':'.join((self.etl_process_name, 'datetime_update'))

    @backoff(exception_class=redis.ConnectionError)
    def check_running_process(self):
        """Метод проверки статуса запуска процесса"""
        return int(self.state.retrieve_state(self.etl_process_name))

    @backoff(exception_class=redis.ConnectionError)
    def get_datetime_update(self) -> str:
        """Метод получения даты обновления данных"""
        return self.state.retrieve_state(self.datetime_update_key)

    def start_elt(self):
        """
        При вызове экземпляра формируем пайплайн процесса в зависимости от имени процесса.
        Если процесс вызван впервые то устанавливаем время обновления текущее время минус примерно 100 лет
        Лимиты для корутин задаю в этом методе, но можно при желании вынести в __init__
        """
        if self.check_running_process():
            logger.warning(msg=f'{self.etl_process_name} etl process already running, wait for the process to finish')
            return
        self.state.save_state(self.etl_process_name, 1)

        self.datetime_update = self.get_datetime_update() or (datetime.now() - timedelta(weeks=5200)).strftime(
            '%Y-%m-%d %H:%M:%S')

        movies_from_transform = self.load.load_data_coroutine(datetime_update_key=self.datetime_update_key, limit=2)
        movies_from_extract = self.transform(movies_from_transform)
        full_data_movies = self.extract.full_data_movies_coroutine(movies_from_extract)
        if self.etl_process_name == 'movies':
            self.extract.main_table_function(datetime_update=self.datetime_update, limit=10,
                                             next_coroutine=full_data_movies)
        else:
            movies = self.extract.related_table_coroutine(limit=10, next_coroutine=full_data_movies)
            self.extract.main_table_function(datetime_update=self.datetime_update, limit=10, next_coroutine=movies)

        self.state.save_state(self.etl_process_name, 0)
        logger.info(f'{self.etl_process_name} elt process is finish')
