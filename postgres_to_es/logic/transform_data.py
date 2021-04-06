from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Coroutine

from helper_modules.utils import init_coroutine


@init_coroutine
def transform_movies_coroutine(next_coroutine: Coroutine):
    """
    Корутина трансформации кинопроизведений
    :param next_coroutine: корутина в которую будет передваться результат трансформации данных,
    в нашем случае в корутину загрузки данных
    :return: None
    """
    try:
        while True:
            movies = yield
            movies_to_load_coroutine = []
            for movie in movies:
                _movie = TransformMovie(*movie)
                _movie.transform_persons()
                movies_to_load_coroutine.append(_movie.__dict__)
            next_coroutine.send(movies_to_load_coroutine)
    except GeneratorExit:
        next_coroutine.close()


class RoleType(Enum):
    """Роли в фильме"""
    actor = 'actor'
    writer = 'writer'
    director = 'director'


@dataclass
class Person:
    """Люди и их атрибуты"""
    id: str
    firstname: str
    lastname: str
    birthdate: datetime
    birthplace: str
    role: RoleType

    def full_name(self):
        return ''.join((self.firstname, self.lastname))


class TransformMovie:
    """Трансформатор кинопроизведений"""

    def __init__(self, idx: str, title: str, description: str, creation_date: datetime, rating: float,
                 imdb_rating: float, movie_type: str, age_limit: int, person_data: List[List[str]],
                 genres: List[str]):
        self.id = idx
        self.title = title
        self.description = description
        self.creation_date = creation_date
        self.rating = rating
        self.imdb_rating = imdb_rating
        self.movie_type = movie_type
        self.age_limit = age_limit
        self.person_data = person_data
        self.genres = genres
        self.actors = []
        self.actors_names = []
        self.writers = []
        self.writers_names = []
        self.directors = []
        self.directors_names = []

    def transform_persons(self):
        """Метод трасформации людей в зависимости от роли в кинопроизведении"""
        for person in self.person_data:
            _person = Person(*person)
            _role = _person.role
            del _person.role
            if _role == 'actor':
                self.actors.append(_person.__dict__)
                self.actors_names.append(_person.full_name())
            elif _role == 'writer':
                self.writers.append(_person.__dict__)
                self.writers_names.append(_person.full_name())
            elif _role == 'director':
                self.directors.append(_person.__dict__)
                self.directors_names.append(_person.full_name())
        del self.person_data
