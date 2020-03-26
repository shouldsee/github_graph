FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7


RUN apt-get update
RUN apt-get install graphviz -y

WORKDIR /app
COPY requirements.txt /app/
RUN python3 -m pip install -r requirements.txt
COPY . /app/
