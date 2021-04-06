"""Настройки для хранилищ"""
import os

dsn_pg = {
    'dbname': os.environ.get('POSTGRES_DB', 'movies'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'port': int(os.environ.get('POSTGRES_PORT', 5432))
}

dsn_es = {
    'host': os.environ.get('ELASTIC_HOST', 'localhost'),
    'port': int(os.environ.get('ELASTIC_PORT', 9200))
}

dsn_red = {
    'host': os.environ.get('REDIS_HOST', 'localhost'),
    'port': int(os.environ.get('REDIS_PORT', 6379))
}