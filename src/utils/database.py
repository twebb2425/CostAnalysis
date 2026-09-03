# Imports Python's built-in operating system tools so Python can access environment variables.
import os

# Imports the function used to load variables from our local .env file.
from dotenv import load_dotenv

# Imports SQLAlchemy's function for creating a reusable database engine.
from sqlalchemy import create_engine


# Defines a reusable function that creates our PostgreSQL database connection.
def get_database_engine():

    # Loads database credentials stored in the project's local .env file.
    load_dotenv()

    # Checks whether a complete database connection URL exists in the environment.
    database_url = os.getenv(
        "DATABASE_URL"
    )

    # Checks whether a complete DATABASE_URL was provided.
    if database_url:

        # Checks whether the URL uses the standard PostgreSQL prefix.
        if database_url.startswith(
            "postgresql://"
        ):

            # Changes the prefix so SQLAlchemy uses Psycopg 3 instead of Psycopg 2.
            database_url = database_url.replace(
                "postgresql://",
                "postgresql+psycopg://",
                1
            )

    # Handles the local development setup when DATABASE_URL is not provided.
    else:

        # Gets the PostgreSQL host from the environment variables.
        db_host = os.getenv(
            "DB_HOST"
        )

        # Gets the PostgreSQL port from the environment variables.
        db_port = os.getenv(
            "DB_PORT"
        )

        # Gets the PostgreSQL database name from the environment variables.
        db_name = os.getenv(
            "DB_NAME"
        )

        # Gets the PostgreSQL username from the environment variables.
        db_user = os.getenv(
            "DB_USER"
        )

        # Gets the PostgreSQL password from the environment variables.
        db_password = os.getenv(
            "DB_PASSWORD"
        )

        # Builds the PostgreSQL connection URL using Psycopg 3.
        database_url = (
            f"postgresql+psycopg://"
            f"{db_user}:{db_password}"
            f"@{db_host}:{db_port}"
            f"/{db_name}"
        )

    # Creates a SQLAlchemy engine using the final PostgreSQL connection URL.
    engine = create_engine(
        database_url
    )

    # Returns the engine so other scripts can reuse the database connection.
    return engine


# Runs this test only when database.py is executed directly.
if __name__ == "__main__":

    # Creates a database engine using the reusable function.
    engine = get_database_engine()

    # Starts a protected block for testing the database connection.
    try:

        # Opens a connection to PostgreSQL.
        with engine.connect() as connection:

            # Confirms that the reusable database connection works.
            print(
                "Reusable database connection successful."
            )

    # Catches any database connection error.
    except Exception as error:

        # Displays the error so we can troubleshoot it.
        print(
            f"Database connection failed: {error}"
        )