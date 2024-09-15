FROM python:3.9-slim-buster

WORKDIR /app

COPY ./app/main.py /app/
COPY ./requirements.txt /app/
COPY ./app/templates /app/templates
COPY ./app/static /app/static
COPY ./src /app/src
COPY ./app/nginx.conf /etc/nginx/nginx.conf
COPY ./app/start.sh /start.sh

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

VOLUME /app/storage

EXPOSE 8080

RUN apt-get update && apt-get install -y nginx

# Run the application
RUN chmod +x /start.sh
CMD ["/start.sh"]
