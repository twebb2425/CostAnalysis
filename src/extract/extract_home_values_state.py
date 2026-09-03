# Imports Path so we can build file paths that work across operating systems.
from pathlib import Path

# Imports requests so Python can download the Zillow CSV file.
import requests

# Imports Pandas so we can inspect the dates in the downloaded Zillow dataset.
import pandas as pd

# Imports our reusable logging function.
from src.utils.logging_utils import get_logger

# Imports our reusable freshness check function.
from src.utils.freshness import check_for_new_home_value_month


# Creates a logger for the state home value extraction module.
logger = get_logger(__name__)


# Finds the root folder of the CostAnalysis project.
PROJECT_ROOT = Path(__file__).resolve().parents[2]


# Builds the full path where the raw Zillow home value dataset will be saved.
OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "home_values_state_raw.csv"
)


# Stores the Zillow State ZHVI CSV download URL.
ZILLOW_URL = (
    "https://files.zillowstatic.com/research/public_csvs/zhvi/"
    "State_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
)


# Defines a reusable function that extracts state-level Zillow home value data.
def extract_home_values_state():

    # Records that the Zillow extraction process is starting.
    logger.info(
        "Starting state home value extraction."
    )

    # Sends a request to download the Zillow State ZHVI CSV file.
    response = requests.get(
        ZILLOW_URL,
        timeout=30
    )

    # Raises an error if Zillow returns an unsuccessful HTTP response.
    response.raise_for_status()

    # Writes the downloaded CSV content directly to the raw data file.
    OUTPUT_PATH.write_bytes(
        response.content
    )

    # Records where the raw Zillow dataset was saved.
    logger.info(
        f"Raw state home value data saved to: {OUTPUT_PATH}"
    )

    # Reads only the column names from the newly downloaded Zillow CSV file.
    zillow_columns = pd.read_csv(
        OUTPUT_PATH,
        nrows=0
    ).columns

    # Creates an empty list that will store valid Zillow monthly date columns.
    date_columns = []

    # Loops through every column name in the Zillow dataset.
    for column in zillow_columns:

        # Attempts to convert the column name into a date.
        parsed_date = pd.to_datetime(
            column,
            format="%Y-%m-%d",
            errors="coerce"
        )

        # Checks whether the column name was successfully recognized as a date.
        if not pd.isna(
            parsed_date
        ):

            # Adds the valid monthly date to our list.
            date_columns.append(
                parsed_date
            )

    # Checks whether Zillow provided any recognizable monthly date columns.
    if not date_columns:

        # Raises an error because the Zillow dataset structure may have changed.
        raise ValueError(
            "No valid monthly date columns were found in the Zillow dataset."
        )

    # Finds the newest monthly date available in the downloaded Zillow data.
    latest_source_date = max(
        date_columns
    )

    # Records the newest date currently available from Zillow.
    logger.info(
        f"Latest Zillow source date: {latest_source_date.date()}."
    )

    # Compares the newest Zillow source date with the newest date already in PostgreSQL.
    new_month_detected = check_for_new_home_value_month(
        latest_source_date
    )

    # Checks whether Zillow has published a newer reporting month.
    if new_month_detected:

        # Records that the downloaded source contains a newly published month.
        logger.info(
            "A new Zillow reporting month is available for processing."
        )

        # Returns True so run_pipeline.py knows to continue the Zillow ETL process.
        return True

    # Handles the case where Zillow has not published a newer reporting month.
    else:

        # Records that no new reporting month was found.
        logger.info(
            "No new Zillow reporting month is currently available."
        )

        # Returns False so run_pipeline.py knows to skip transformation and loading.
        return False


# Runs the extraction only when this file is executed directly.
if __name__ == "__main__":

    # Calls the reusable Zillow state home value extraction function.
    extract_home_values_state()