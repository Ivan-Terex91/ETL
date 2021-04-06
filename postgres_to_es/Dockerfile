FROM python:3.8.5-alpine

WORKDIR /usr/src/postgres_to_es


COPY . .

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev curl

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/postgres_to_es"

