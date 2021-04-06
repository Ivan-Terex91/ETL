"""В этом модуле вынесены отдельно вспомогательные функции для sql запросов"""


def query_formatter(table_name: str, table_alias: str) -> str:
    """
    Функция для формирования простого sql запроса к определённой таблице
    :param table_name: имя таблицы
    :param table_alias: псевнодим таблицы
    :return: sql запрос заданной таблицы
    """
    query_pattern = f"""
    SELECT {table_alias}.id, {table_alias}.modified
    FROM content.{table_name} AS {table_alias} 
    WHERE {table_alias}.modified > %s
    ORDER BY {table_alias}.modified, {table_alias}.id
    OFFSET %s LIMIT %s
    """
    return query_pattern


def query_rel_formatter(main_table_name: str, main_table_alias: str, related_table_name: str, related_table_alias: str,
                        relation: str) -> str:
    """
    Функция для формирования sql запроса к связанным таблицам
    :param main_table_name: имя главной таблиуы
    :param main_table_alias: псевдоним главной таблицы
    :param related_table_name: имя связанной таблицы
    :param related_table_alias: псевдоним связанной таблицы
    :param relation: имя столбца для проверки на вхождение
    :return: sql запрос для заданных таблиц
    """
    query_pattern = f"""
              SELECT DISTINCT {main_table_alias}.id as movie_id, {main_table_alias}.modified
              FROM content.{main_table_name} AS {main_table_alias}
              LEFT JOIN content.{related_table_name} AS {related_table_alias}
              ON {related_table_alias}.movie_id = {main_table_alias}.id
              WHERE {related_table_alias}.{relation}_id IN %s
              ORDER BY {main_table_alias}.modified, {main_table_alias}.id
              OFFSET %s LIMIT %s;
                """
    return query_pattern


def query_full_data_movies() -> str:
    """Sql запрос на выборку полных данных по фильму"""
    query = """SELECT movie.id as movie_id, movie.title, movie.description, movie.creation_date::varchar, movie.rating, 
    movie.imdb_rating, movie.movie_type, movie.age_limit, array_agg(distinct (array[person.id::varchar, 
    person.firstname, person.lastname, person.birthdate::varchar, person.birthplace, movieperson.role])) as person_data,
    array_agg(distinct genre.name) as genres
    FROM content.movies_movie AS movie
    LEFT JOIN content.movies_movieperson AS movieperson
    ON movieperson.movie_id = movie.id
    LEFT JOIN content.movies_person AS person
    ON person.id = movieperson.person_id
    LEFT JOIN content.movies_movie_genres AS moviegenre
    ON moviegenre.movie_id = movie.id
    LEFT JOIN content.movies_genre AS genre
    ON genre.id = moviegenre.genre_id
    WHERE movie.id IN %s
    GROUP BY movie.id
    ORDER BY movie.id;"""

    return query
