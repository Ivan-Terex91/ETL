import time

from elt_pipelines import ETLPipelines

if __name__ == '__main__':
    movies_elt = ETLPipelines(etl_process_name='movies', table_name='movies_movie', table_alias='movie')
    genres_etl = ETLPipelines(etl_process_name='genres', table_name='movies_genre', table_alias='genre',
                              main_table_name='movies_movie', main_table_alias='movie',
                              related_table_name='movies_movie_genres',
                              related_table_alias='movie_genres', relation='genre')
    persons_etl = ETLPipelines(etl_process_name='persons', table_name='movies_person', table_alias='person',
                               main_table_name='movies_movie', main_table_alias='movie',
                               related_table_name='movies_movieperson',
                               related_table_alias='movieperson', relation='person')
    while True:
        genres_etl()
        time.sleep(10)
        movies_elt()
        time.sleep(10)
        persons_etl()
        time.sleep(10)