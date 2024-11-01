import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
from sqlmodel import SQLModel, Field, create_engine
from sqlalchemy import text
from typing import Optional
from datetime import datetime


def server_engine():

    database = os.getenv("SERVER_DB")
    username = os.getenv("SERVER_USER")
    password = os.getenv("SERVER_PWRD")
    host = os.getenv("SERVER_HOST")
    port = os.getenv("SERVER_PORT")

    # Create PostgreSQL connection string
    connection_string = f'postgresql://{username}:{password}@{host}:{port}/{database}'

    # Create and return the engine
    engine = create_engine(connection_string)

    return engine

engine = server_engine()

# Make sure the DB is connected
with engine.connect() as connection:
    result = connection.execute(text("SELECT usename FROM pg_user;"))
    for row in result:
        print(f"Username: {row[0]}")
