# Imports Pandas so we can read the processed Zillow CSV file.
import pandas as pd

# Imports SQLAlchemy text so we can execute SQL statements safely.
from sqlalchemy import text

# Imports Path so we can build file paths that work across operating systems.
from pathlib import Path

# Imports our reusable database connection function.
from src.utils.database import get_database_engine

# Imports our reusable DataFrame validation function.
from src.utils.validation import validate_dataframe

# Imports our reusable logging function.
from src.utils.logging_utils import get_logger


# Creates a logger for the state home value loading module.
logger = get_logger(__name__)


# Finds the root folder of the CostAnalysis project.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Builds the path to the processed Zillow state home value dataset.
PROCESSED_FILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "home_values_state.csv"
)


# Defines a reusable function that loads state home values into PostgreSQL.
def load_home_values_state():

    # Records that the state home value load process is starting.
    logger.info("Starting state home value load.")

    # Loads the processed Zillow CSV file into a Pandas DataFrame.
    home_values_df = pd.read_csv(
        PROCESSED_FILE_PATH
    )

    # Converts the date column back into Pandas datetime values.
    home_values_df["date"] = pd.to_datetime(
        home_values_df["date"],
        format="%Y-%m-%d"
    )

    # Defines the columns that must exist before the dataset can be loaded.
    required_columns = [
        "region_id",
        "geography_type",
        "state_name",
        "date",
        "home_value",
    ]

    # Validates that the dataset contains the required columns and is not empty.
    validated_rows = validate_dataframe(
        home_values_df,
        required_columns
    )

    # Records how many rows passed validation.
    logger.info(
        f"Validated {validated_rows} state home value rows for loading."
    )

    # Creates the PostgreSQL database engine.
    engine = get_database_engine()

    # Opens a database transaction that commits automatically if successful.
    with engine.begin() as connection:

        # Creates the permanent state home value table if it does not already exist.
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS home_values_state (
                    region_id INTEGER NOT NULL,
                    geography_type VARCHAR(20) NOT NULL,
                    state_name VARCHAR(100) NOT NULL,
                    date DATE NOT NULL,
                    home_value DOUBLE PRECISION,
                    PRIMARY KEY (region_id, date)
                )
                """
            )
        )

        # Removes the temporary staging table if one was left from a previous run.
        connection.execute(
            text(
                """
                DROP TABLE IF EXISTS home_values_state_staging
                """
            )
        )

        # Creates an empty temporary staging table with the same structure as the permanent table.
        connection.execute(
            text(
                """
                CREATE TEMP TABLE home_values_state_staging (
                    region_id INTEGER NOT NULL,
                    geography_type VARCHAR(20) NOT NULL,
                    state_name VARCHAR(100) NOT NULL,
                    date DATE NOT NULL,
                    home_value DOUBLE PRECISION
                )
                """
            )
        )

        # Loads the processed Zillow DataFrame into the temporary staging table.
        home_values_df.to_sql(
            name="home_values_state_staging",
            con=connection,
            if_exists="append",
            index=False
        )

        # Inserts new records and updates records that already have the same region ID and date.
        connection.execute(
            text(
                """
                INSERT INTO home_values_state (
                    region_id,
                    geography_type,
                    state_name,
                    date,
                    home_value
                )
                SELECT
                    region_id,
                    geography_type,
                    state_name,
                    date,
                    home_value
                FROM home_values_state_staging
                ON CONFLICT (region_id, date)
                DO UPDATE SET
                    geography_type = EXCLUDED.geography_type,
                    state_name = EXCLUDED.state_name,
                    home_value = EXCLUDED.home_value
                """
            )
        )

    # Records that the upsert process completed successfully.
    logger.info(
        f"Successfully processed {len(home_values_df)} rows into home_values_state."
    )

    # Returns the number of source rows that were processed.
    return len(home_values_df)


# Runs the load function only when this file is executed directly.
if __name__ == "__main__":

    # Calls the reusable state home value loading function.
    load_home_values_state()