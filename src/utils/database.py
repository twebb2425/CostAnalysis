# Import the OS system tool so Python can access enviroment variables
import os

# imports the function useed to load varibales from our .env file
from dotenv import load_dotenv

# import the SQL Alchemy function for creating a database engine
from sqlalchemy import create_engine

# create a reusable function that creates our PostgreSQL database connection
def get_database_engine():
    # Loads the database credentials stored in the project's .env file.
    load_dotenv()

    # Gets the PostgreSQL host from the environment variables.
    db_host = os.getenv("DB_HOST")

    # Gets the PostgreSQL port from the environment variables.
    db_port = os.getenv("DB_PORT")

    # Gets the PostgreSQL database name from the environment variables.
    db_name = os.getenv("DB_NAME")

    # Gets the PostgreSQL username from the environment variables.
    db_user = os.getenv("DB_USER")

    # Gets the PostgreSQL password from the environment variables.
    db_password = os.getenv("DB_PASSWORD")

    # Builds the PostgreSQL connection URL using our environment variables.
    database_url = f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    # Creates a SQLAlchemy engine using the PostgreSQL connection URL.
    engine = create_engine(database_url)

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
            print("Reusable database connection successful.")

    # Catches any database connection error.
    except Exception as error:

        # Displays the error so we can troubleshoot it.
        print(f"Database connection failed: {error}")