# Imports Python's operating system tools so we can read environment variables.
import os

# Imports Pandas so we can move table data between PostgreSQL databases.
import pandas as pd

# Imports dotenv so Python can read values stored in the .env file.
from dotenv import load_dotenv

# Imports SQLAlchemy's function for creating database engines.
from sqlalchemy import create_engine


# Loads variables stored in the project's .env file.
load_dotenv()


# Gets the local PostgreSQL host from the environment variables.
local_db_host = os.getenv(
    "DB_HOST"
)


# Gets the local PostgreSQL port from the environment variables.
local_db_port = os.getenv(
    "DB_PORT"
)


# Gets the local PostgreSQL database name from the environment variables.
local_db_name = os.getenv(
    "DB_NAME"
)


# Gets the local PostgreSQL username from the environment variables.
local_db_user = os.getenv(
    "DB_USER"
)


# Gets the local PostgreSQL password from the environment variables.
local_db_password = os.getenv(
    "DB_PASSWORD"
)


# Builds the SQLAlchemy connection URL for the local PostgreSQL database.
local_database_url = (
    f"postgresql+psycopg://"
    f"{local_db_user}:{local_db_password}"
    f"@{local_db_host}:{local_db_port}"
    f"/{local_db_name}"
)


# Gets the Supabase PostgreSQL connection URL from the environment variables.
supabase_database_url = os.getenv(
    "SUPABASE_DATABASE_URL"
)


# Stops the script if the Supabase connection string is missing.
if not supabase_database_url:

    # Raises an error explaining the missing environment variable.
    raise ValueError(
        "SUPABASE_DATABASE_URL was not found in the .env file."
    )


# Checks whether the Supabase connection string uses the standard PostgreSQL prefix.
if supabase_database_url.startswith(
    "postgresql://"
):

    # Replaces the standard PostgreSQL prefix so SQLAlchemy uses Psycopg 3.
    supabase_database_url = supabase_database_url.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )


# Creates the SQLAlchemy engine for the local PostgreSQL database.
local_engine = create_engine(
    local_database_url
)


# Creates the SQLAlchemy engine for the Supabase PostgreSQL database.
supabase_engine = create_engine(
    supabase_database_url
)


# Reads the complete housing_costs table from the local PostgreSQL database.
housing_costs_df = pd.read_sql_table(
    "housing_costs",
    local_engine
)


# Records how many housing cost rows were found locally.
print(
    f"Local housing_costs rows found: {len(housing_costs_df)}"
)


# Reads the complete home_values_state table from the local PostgreSQL database.
home_values_df = pd.read_sql_table(
    "home_values_state",
    local_engine
)


# Records how many home value rows were found locally.
print(
    f"Local home_values_state rows found: {len(home_values_df)}"
)


# Writes the housing_costs DataFrame into Supabase PostgreSQL.
housing_costs_df.to_sql(
    "housing_costs",
    supabase_engine,
    if_exists="replace",
    index=False
)


# Records that the housing_costs migration completed successfully.
print(
    "housing_costs migrated to Supabase successfully."
)


# Writes the home_values_state DataFrame into Supabase PostgreSQL.
home_values_df.to_sql(
    "home_values_state",
    supabase_engine,
    if_exists="replace",
    index=False,
    chunksize=1000
)


# Records that the home_values_state migration completed successfully.
print(
    "home_values_state migrated to Supabase successfully."
)


# Reads the migrated housing_costs table back from Supabase for verification.
supabase_housing_costs_df = pd.read_sql_table(
    "housing_costs",
    supabase_engine
)


# Reads the migrated home_values_state table back from Supabase for verification.
supabase_home_values_df = pd.read_sql_table(
    "home_values_state",
    supabase_engine
)


# Displays the number of housing_cost rows stored in Supabase.
print(
    f"Supabase housing_costs rows: {len(supabase_housing_costs_df)}"
)


# Displays the number of home value rows stored in Supabase.
print(
    f"Supabase home_values_state rows: {len(supabase_home_values_df)}"
)


# Confirms that the complete database migration finished successfully.
print(
    "Supabase migration completed successfully."
)
