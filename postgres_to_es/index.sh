#!/bin/sh
curl -XPUT es:9200/movies -H 'Content-Type: application/json' -d '

{
  "settings": {
    "refresh_interval": "1s",
    "analysis": {
      "filter": {
        "english_stop": {
          "type": "stop",
          "stopwords": "_english_"
        },
        "english_stemmer": {
          "type": "stemmer",
          "language": "english"
        },
        "english_possessive_stemmer": {
          "type": "stemmer",
          "language": "possessive_english"
        },
        "russian_stop": {
          "type": "stop",
          "stopwords": "_russian_"
        },
        "russian_stemmer": {
          "type": "stemmer",
          "language": "russian"
        }
      },
      "analyzer": {
        "ru_en": {
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "english_stop",
            "english_stemmer",
            "english_possessive_stemmer",
            "russian_stop",
            "russian_stemmer"
          ]
        }
      }
    }
  },
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "id": {
        "type": "keyword"
      },
      "title": {
        "type": "text",
        "analyzer": "ru_en",
        "fields": {
          "raw": {
            "type": "keyword"
          }
        }
      },
      "description": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "creation_date": {
        "type": "date"
      },
      "rating": {
        "type": "float"
      },
      "imdb_rating": {
        "type": "float"
      },
      "movie_type": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "age_limit":{
        "type": "integer"
      },
      "genres": {
        "type": "keyword"
      },
      "actors_names": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "writers_names": {
        "type": "text",
        "analyzer": "ru_en"
      },
       "directors_names": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "actors": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "id": {
            "type": "keyword"
          },
          "firstname": {
            "type": "text",
            "analyzer": "ru_en"
          },
          "lastname": {
            "type": "text",
            "analyzer": "ru_en"
          },
          "birthdate": {
            "type": "date"
          },
          "birthplace": {
            "type": "text",
            "analyzer": "ru_en"
          }
        }
      },
      "writers": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "id": {
            "type": "keyword"
          },
          "firstname": {
            "type": "text",
            "analyzer": "ru_en"
          },
          "lastname": {
            "type": "text",
            "analyzer": "ru_en"
          },
          "birthdate": {
            "type": "date"
          },
          "birthplace": {
            "type": "text",
            "analyzer": "ru_en"
          }
        }
      },
      "directors": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "id": {
            "type": "keyword"
          },
          "firstname": {
            "type": "text",
            "analyzer": "ru_en"
          },
          "lastname": {
            "type": "text",
            "analyzer": "ru_en"
          },
          "birthdate": {
            "type": "date"
          },
          "birthplace": {
            "type": "text",
            "analyzer": "ru_en"
          }
        }
      }
    }
  }
} '


