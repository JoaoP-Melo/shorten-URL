FROM python:3.14-slim

WORKDIR /src

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .