FROM python:3.9-slim-buster

WORKDIR /app

COPY . /app /app

RUN pip install -r /app/requirements.txt

RUN adduser --disabled-password --gecos '' appuser
USER appuser

EXPOSE 8080

# Run the application
CMD ["gunicorn", "--chdir", "/app", "-b", "0.0.0.0:8080", "main:app"]
