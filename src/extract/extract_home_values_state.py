# Imports Path so the project can build file paths that work on both macOS and GitHub Actions.
from pathlib import Path

# Imports Pandas so we can inspect the Zillow CSV file.
import pandas as pd

# Imports Requests so we can download the Zillow dataset from the internet.
import requests

# Imports the reusable freshness check for Zillow home value data.
from src.utils.freshness import check_for_new_home_value_month

# Imports the reusable project logger.
from src.utils.logging_utils import get_logger


# Creates a logger specifically for this module.
logger = get_logger(
    __name__
)


# Finds the root directory of the CostAnalysis project.
PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


# Defines the directory where raw source files are stored.
RAW_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
)


# Defines the path where the raw Zillow CSV file will be saved.
OUTPUT_PATH = (
    RAW_DATA_DIR
    / "home_values_state_raw.csv"
)


# Defines the Zillow URL for state-level home value data.
ZILLOW_URL = (
    "https://files.zillowstatic.com/research/public_csvs/"
    "zhvi/State_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
)


# Defines the function responsible for extracting Zillow state home value data.
def extract_home_values_state():

    # Records that the Zillow extraction process has started.
    logger.info(
        "Starting state home value extraction."
    )

    # Creates the raw data directory if it does not already exist.
    #
    # This is especially important for GitHub Actions because each workflow
    # starts on a fresh virtual machine and empty directories are not stored
    # by Git.
    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Downloads the current Zillow state home value dataset.
    response = requests.get(
        ZILLOW_URL,
        timeout=60
    )

    # Raises an exception if Zillow returned an unsuccessful HTTP response.
    response.raise_for_status()

    # Writes the downloaded Zillow CSV file into the project's raw data directory.
    OUTPUT_PATH.write_bytes(
        response.content
    )

    # Records where the raw Zillow file was saved.
    logger.info(
        f"Raw state home value data saved to: {OUTPUT_PATH}"
    )

    # Reads only the header row from the downloaded Zillow CSV file.
    #
    # We only need the column names at this stage because the Zillow reporting
    # dates are stored as columns in the source dataset.
    source_columns = pd.read_csv(
        OUTPUT_PATH,
        nrows=0
    ).columns

    # Creates an empty list that will contain valid Zillow reporting dates.
    source_dates = []

    # Loops through every column name in the Zillow dataset.
    for column in source_columns:

        # Attempts to convert the column name into a date.
        parsed_date = pd.to_datetime(
            column,
            errors="coerce"
        )

        # Checks whether Pandas successfully recognized the column as a date.
        if not pd.isna(
            parsed_date
        ):

            # Adds the valid reporting date to the list.
            source_dates.append(
                parsed_date
            )

    # Stops the pipeline if no reporting-date columns were found.
    if not source_dates:

        # Raises an error because Zillow data cannot be evaluated without dates.
        raise ValueError(
            "No Zillow reporting dates were found in the source dataset."
        )

    # Finds the most recent reporting date available from Zillow.
    latest_source_date = max(
        source_dates
    )

    # Records the latest reporting date found in the Zillow source.
    logger.info(
        f"Latest Zillow source date: {latest_source_date.date()}."
    )

    # Compares Zillow's newest reporting date against the newest date
    # currently stored in PostgreSQL.
    new_home_value_data = check_for_new_home_value_month(
        latest_source_date
    )

    # Checks whether Zillow has released a newer reporting month.
    if not new_home_value_data:

        # Records that no new Zillow reporting month needs to be processed.
        logger.info(
            "No new Zillow reporting month is currently available."
        )

        # Returns False so run_pipeline.py knows to skip transform and load.
        return False

    # Records that a new Zillow reporting month has been detected.
    logger.info(
        "New Zillow reporting month detected."
    )

    # Returns True so run_pipeline.py knows to continue transform and load.
    return True


# Runs the extraction function only when this file is executed directly.
if __name__ == "__main__":

    # Executes the Zillow state home value extraction process.
    extract_home_values_state()