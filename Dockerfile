FROM python:3.9-slim-buster

WORKDIR /app

COPY ./app/main.py /app/
COPY ./requirements.txt /app/
COPY ./app/templates /app/templates
COPY ./app/static /app/static
COPY ./src /app/src
COPY nginx.conf /etc/nginx/nginx.conf

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

VOLUME /app/storage

EXPOSE 8080
ENV FLASK_APP=app.py

# Run the application
CMD ["gunicorn", "--chdir", "/app", "-b", "0.0.0.0:8080", "main:app"]
