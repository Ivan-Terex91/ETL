FROM python:3.8.5-alpine

WORKDIR /usr/src/sqlite_to_postgres

COPY . .

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt



