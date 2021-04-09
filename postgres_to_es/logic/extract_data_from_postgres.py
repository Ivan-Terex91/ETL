import logging.config

import psycopg2
import redis
from typing import Coroutine

from helper_modules.utils import LOGGING_CONFIG
from helper_modules.saving_state import RedisStorage
from helper_modules.utils import backoff, init_coroutine
from helper_modules.sql_helper import query_formatter, query_rel_formatter, query_full_data_movies

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('app_logger')


class PostgresLoader:
    """Класс загрузки данных из postgresql.
    Класс аккамулирует в себе методы для загрузки данных из БД"""

    def __init__(self, dsn, elt_process_name: str):
        self.dsn_pg = dsn
        self.redis = redis.Redis
        self.state = RedisStorage(self.redis)
        self.name_key = 'current_offset'
        self.etl_process_name = elt_process_name
        self.config_tables = self.tables_names_for_extract

    @backoff(exception_class=psycopg2.Error)
    def main_table_function(self, datetime_update: str,
                            limit: int, next_coroutine: Coroutine):
        """
         Метод для загрузки обновлённых данных из таблицы, в зависимости от ETL процесса и имени таблицы.
         :param datetime_update: последнее время обновления записей в таблице
         :param limit: лимит записей которые будем брать
         :param next_coroutine: корутина в которую будет передваться результат запроса
         :return: None
        """

        while True:
            storage_key = ':'.join((self.etl_process_name, self.config_tables.get('table_alias'), self.name_key))
            curr_offset = int(self.state.retrieve_state(storage_key))
            with psycopg2.connect(**self.dsn_pg) as connection:
                cursor = connection.cursor()

                query = query_formatter(table_name=self.config_tables.get('table_name'),
                                        table_alias=self.config_tables.get('table_alias'))
                cursor.execute(query, (datetime_update, curr_offset, limit))
                result = cursor.fetchall()
                if result:
                    params_for_next_coroutine = []
                    try:
                        for param in result:
                            params_for_next_coroutine.append(param[0])
                        next_coroutine.send(params_for_next_coroutine)

                    except GeneratorExit:
                        next_coroutine.close()
                    except StopIteration:
                        self.state.save_state(':'.join((self.etl_process_name, 'datetime_update')), datetime_update)
                        next_coroutine.close()
                        logger.warning(
                            msg=f'Extracted not all updated records from the table {self.config_tables.get("table_name")}')
                        return

                    self.state.save_state(storage_key, curr_offset + len(params_for_next_coroutine))
                else:
                    logger.info(
                        msg=f'Extracted all updated records from the table {self.config_tables.get("table_name")}')
                    logger.info(msg=f'quantity of updated records {int(self.state.retrieve_state(storage_key))}')
                    self.state.save_state(storage_key, 0)
                    return

    @backoff(exception_class=psycopg2.Error)
    @init_coroutine
    def related_table_coroutine(self, limit: int, next_coroutine: Coroutine):
        """
        Корутина для загрузки данных из связанной таблицы, в зависимости от ETL процесса и имён главной
        и связанной таблицы.
        :param limit: лимит записей которые будем брать
        :param next_coroutine: корутина в которую будет передваться результат запроса
        :return: None
        """
        storage_key = ":".join((self.etl_process_name, self.config_tables.get('main_table_alias'),
                                self.config_tables.get('related_table_alias'), self.name_key))
        try:
            while True:
                params_from_prev_coroutine = yield
                curr_offset = int(self.state.retrieve_state(storage_key))
                with psycopg2.connect(**self.dsn_pg) as connection:
                    cursor = connection.cursor()

                    related_query = query_rel_formatter(main_table_name=self.config_tables.get('main_table_name'),
                                                        main_table_alias=self.config_tables.get('main_table_alias'),
                                                        related_table_name=self.config_tables.get('related_table_name'),
                                                        related_table_alias=self.config_tables.get(
                                                            'related_table_alias'),
                                                        relation=self.config_tables.get('relation'))

                    if params_from_prev_coroutine:
                        params_for_next_coroutine = []
                        while True:
                            cursor.execute(related_query, (tuple(params_from_prev_coroutine), curr_offset, limit))
                            result = cursor.fetchall()

                            if not result:
                                break

                            for param in result:
                                params_for_next_coroutine.append(param[0])

                            curr_offset = curr_offset + len(result)
                            next_coroutine.send(params_for_next_coroutine)
                            self.state.save_state(storage_key, curr_offset + len(params_for_next_coroutine))
                    self.state.save_state(storage_key, 0)
        except GeneratorExit:
            self.state.save_state(storage_key, 0)
            next_coroutine.close()

    @backoff(exception_class=psycopg2.Error)
    @init_coroutine
    def full_data_movies_coroutine(self, next_coroutine: Coroutine):
        """
        Метод загрузки недостоющей информации по кинопроизведениям
        :param next_coroutine: корутина в которую будет передваться результат запроса, в нашем случае в корутину
        трансформации данных
        :return: None
        """

        try:
            while True:
                movie_list = yield
                with psycopg2.connect(**self.dsn_pg) as connection:
                    cursor = connection.cursor()
                    full_data_movie_list = []
                    full_data_movies_query = query_full_data_movies()

                    if movie_list:
                        cursor.execute(full_data_movies_query, (tuple(movie_list),))

                        for full_data_movie in cursor.fetchall():
                            full_data_movie_list.append(full_data_movie)

                    next_coroutine.send(full_data_movie_list)
        except GeneratorExit:
            next_coroutine.close()

    @property
    def tables_names_for_extract(self):
        """Конфигурация имён таблиц в БД в зависимости от etl процесса"""
        config_table_names = {
            'movies': {'table_name': 'movies_movie', 'table_alias': 'movie', },
            'genres': {'table_name': 'movies_genre', 'table_alias': 'genre',
                       'main_table_name': 'movies_movie', 'main_table_alias': 'movie',
                       'related_table_name': 'movies_movie_genres',
                       'related_table_alias': 'movie_genres', 'relation': 'genre'},
            'persons': {'table_name': 'movies_person', 'table_alias': 'person',
                        'main_table_name': 'movies_movie', 'main_table_alias': 'movie',
                        'related_table_name': 'movies_movieperson',
                        'related_table_alias': 'movieperson', 'relation': 'person'}
        }

        return config_table_names.get(self.etl_process_name)
