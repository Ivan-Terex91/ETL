import time

from logic.elt_pipelines import ETLPipelines
from logic.extract_data_from_postgres import PostgresLoader
from logic.load_to_elastic import ESLoader
from logic.transform_data import transform_movies_coroutine
from settings import dsn_pg, dsn_es

if __name__ == '__main__':

    movies_elt = ETLPipelines(etl_process_name='movies', extract=PostgresLoader(dsn_pg, 'movies'),
                              transform=transform_movies_coroutine,
                              load=ESLoader(dsn_es))
    genres_etl = ETLPipelines(etl_process_name='genres', extract=PostgresLoader(dsn_pg, 'genres'),
                              transform=transform_movies_coroutine,
                              load=ESLoader(dsn_es))
    persons_etl = ETLPipelines(etl_process_name='persons', extract=PostgresLoader(dsn_pg, 'persons'),
                               transform=transform_movies_coroutine,
                               load=ESLoader(dsn_es))
    while True:
        genres_etl.start_elt()
        movies_elt.start_elt()
        persons_etl.start_elt()
        time.sleep(10)
