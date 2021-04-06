import redis
from datetime import datetime, timedelta
import logging

from extract_data_from_postgres import PostgresLoader
from helper_modules.saving_state import RedisStorage
from transform_data import transform_movies_coroutine
from load_to_elastic import ESLoader
from settings import dsn_pg, dsn_es
from helper_modules.utils import backoff

logger = logging.getLogger('app_logger')


class ETLPipelines:
    """
    Класс формирующий пайплайны.
    Принимает все необходимые параметры для формирования etl процессов в виде пайплайнов.
    """

    def __init__(self, etl_process_name, table_name, table_alias, main_table_name=None, main_table_alias=None,
                 related_table_name=None, related_table_alias=None, relation=None):
        """
        :param etl_process_name: имя ETL процесса
        :param table_name: имя таблицы
        :param table_alias: псевдоним таблицы
        :param main_table_name: имя главной таблицы
        :param main_table_alias: псевдоним главной таблицы
        :param related_table_name: имя связанной таблицы
        :param related_table_alias: псевдоним связанной таблицы
        :param relation: имя столбца для проверки на вхождение
        """
        self.extract = PostgresLoader(dsn_pg)
        self.transform = transform_movies_coroutine
        self.load = ESLoader(dsn_es)
        self.redis = redis.Redis
        self.state = RedisStorage(self.redis)
        self.etl_process_name = etl_process_name
        self.table_name = table_name
        self.table_alias = table_alias
        self.main_table_name = main_table_name
        self.main_table_alias = main_table_alias
        self.related_table_name = related_table_name
        self.related_table_alias = related_table_alias
        self.relation = relation
        self.datetime_update_key = ':'.join((self.etl_process_name, 'datetime_update'))

    @backoff(exception_class=redis.ConnectionError)
    def check_running_process(self):
        """Метод проверки статуса запуска процесса"""
        return int(self.state.retrieve_state(self.etl_process_name))

    @backoff(exception_class=redis.ConnectionError)
    def get_datetime_update(self) -> str:
        """Метод получения даты обновления данных"""
        return self.state.retrieve_state(self.datetime_update_key)

    def __call__(self):
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
            self.extract.main_table_function(etl_process_name=self.etl_process_name, table_name=self.table_name,
                                             table_alias=self.table_alias, datetime_update=self.datetime_update,
                                             limit=10, next_coroutine=full_data_movies)
        else:
            movies = self.extract.related_table_coroutine(etl_process_name=self.etl_process_name,
                                                          main_table_name=self.main_table_name,
                                                          main_table_alias=self.main_table_alias,
                                                          related_table_name=self.related_table_name,
                                                          related_table_alias=self.related_table_alias,
                                                          relation=self.relation,
                                                          limit=10,
                                                          next_coroutine=full_data_movies)
            self.extract.main_table_function(etl_process_name=self.etl_process_name, table_name=self.table_name,
                                             table_alias=self.table_alias, datetime_update=self.datetime_update,
                                             limit=10, next_coroutine=movies)

        self.state.save_state(self.etl_process_name, 0)
        logger.info(f'{self.etl_process_name} elt process is finish')
