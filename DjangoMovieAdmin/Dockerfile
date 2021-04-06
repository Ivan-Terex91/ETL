FROM python:3.8.5-alpine

WORKDIR /home/app/DjangoMovieAdmin

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev


RUN pip install --upgrade pip
COPY ./requirements .
RUN pip install --no-cache-dir -r production.txt

COPY . .
