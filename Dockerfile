FROM python:3.9-slim-buster

WORKDIR /app

# Install nginx
RUN apt-get update && \
    apt-get install -y nginx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

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

RUN mkdir -p /app/storage && chown -R www-data:www-data /app/storage
RUN echo '#!/bin/bash\nnginx\ngunicorn --chdir /app -b 127.0.0.1:5000 main:app' > /start.sh && \
    chmod +x /start.sh

CMD ["/start.sh"]
