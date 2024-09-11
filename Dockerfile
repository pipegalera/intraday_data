FROM python:3.9-slim-buster

WORKDIR /app

COPY ./app/main.py /app/
COPY ./app/requirements.txt /app/
COPY ./app/templates /app/templates

RUN pip install -r /app/requirements.txt

VOLUME /app/storage

EXPOSE 8080
ENV FLASK_APP=app.py

# Run the application
CMD ["gunicorn", "--chdir", "/app", "-b", "0.0.0.0:8080", "main:app"]
