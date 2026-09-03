# Imports Python's operating system tools so the Census API key can be read from environment variables.
import os

# Imports the current date so the extractor can search for the newest available ACS dataset year.
from datetime import datetime

# Imports Path so file paths work consistently on macOS and GitHub Actions.
from pathlib import Path

# Imports sleep so the extractor can pause briefly between failed Census API requests.
from time import sleep

# Imports Pandas so Census API results can be converted into a DataFrame.
import pandas as pd

# Imports Requests so the extractor can communicate with the Census API.
import requests

# Imports dotenv so local environment variables can be loaded from the project's .env file.
from dotenv import load_dotenv

# Imports the reusable Census rent freshness check.
from src.utils.freshness import check_for_new_rent_year

# Imports the reusable project logger.
from src.utils.logging_utils import get_logger


# Loads environment variables stored in the local .env file.
load_dotenv()


# Creates a logger specifically for this module.
logger = get_logger(
    __name__
)


# Finds the root directory of the CostAnalysis project.
PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


# Defines the directory where raw source data will be stored.
RAW_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
)


# Defines the file path where the raw Census rent dataset will be saved.
OUTPUT_PATH = (
    RAW_DATA_DIR
    / "housing_costs_raw.csv"
)


# Gets the Census API key from the environment variables.
CENSUS_API_KEY = os.getenv(
    "CENSUS_API_KEY"
)


# Defines the Census variable representing median gross rent.
RENT_VARIABLE = "B25064_001E"


# Defines a reusable function for making Census API requests with automatic retries.
def get_census_response(
    api_url,
    parameters,
    max_attempts=3
):

    # Loops through each allowed Census API request attempt.
    for attempt in range(
        1,
        max_attempts + 1
    ):

        # Starts a protected block for the Census API request.
        try:

            # Sends the HTTP request to the Census API with a 60-second timeout.
            response = requests.get(
                api_url,
                params=parameters,
                timeout=60
            )

            # Checks whether the Census endpoint does not exist for the requested year.
            if response.status_code == 404:

                # Returns the response so the calling function can try an earlier ACS year.
                return response

            # Checks whether the Census API returned a temporary server-side error.
            if response.status_code >= 500:

                # Raises an HTTP error so the request can be retried.
                response.raise_for_status()

            # Raises an exception for other unsuccessful HTTP responses.
            response.raise_for_status()

            # Returns the successful Census API response.
            return response

        # Handles network errors, timeouts, and unsuccessful HTTP requests.
        except requests.RequestException as error:

            # Records which Census request attempt failed.
            logger.warning(
                f"Census API request attempt {attempt} of "
                f"{max_attempts} failed: {error}"
            )

            # Checks whether another retry attempt is still available.
            if attempt < max_attempts:

                # Calculates an increasing delay before the next retry.
                wait_seconds = attempt * 5

                # Records how long the extractor will wait before retrying.
                logger.info(
                    f"Waiting {wait_seconds} seconds before retrying "
                    f"the Census API."
                )

                # Pauses execution before making the next Census request.
                sleep(
                    wait_seconds
                )

            # Handles the final failed Census API request.
            else:

                # Records that all retry attempts have been exhausted.
                logger.error(
                    "Census API request failed after all retry attempts."
                )

                # Raises the original request error so GitHub Actions reports the failure correctly.
                raise


# Defines a function that determines the newest available ACS 5-year dataset.
def get_latest_acs_year():

    # Gets the current calendar year.
    current_year = datetime.now().year

    # Creates a test Census API request containing only the median rent variable.
    test_parameters = {
        "get": RENT_VARIABLE,
        "for": "state:*"
    }

    # Adds the Census API key when one is available.
    if CENSUS_API_KEY:

        # Adds the Census API key to the request parameters.
        test_parameters[
            "key"
        ] = CENSUS_API_KEY

    # Searches the current year and the four previous years for an available ACS dataset.
    for census_year in range(
        current_year,
        current_year - 5,
        -1
    ):

        # Builds the Census ACS 5-year API URL for the year being tested.
        api_url = (
            f"https://api.census.gov/data/"
            f"{census_year}/acs/acs5"
        )

        # Sends the test request using the reusable retry function.
        response = get_census_response(
            api_url,
            test_parameters
        )

        # Checks whether the requested ACS dataset exists and returned successfully.
        if response.status_code == 200:

            # Records the newest available ACS 5-year dataset year.
            logger.info(
                f"Latest ACS 5-year dataset found: {census_year}"
            )

            # Returns the newest available Census year.
            return census_year

        # Records that the tested ACS year was not available.
        logger.info(
            f"ACS 5-year dataset not available for {census_year}."
        )

    # Raises an error if no ACS dataset could be found within the search window.
    raise RuntimeError(
        "Unable to locate an available ACS 5-year dataset "
        "within the last five years."
    )


# Defines the main Census rent extraction function.
def extract_housing_data():

    # Finds the newest available ACS 5-year dataset year.
    census_year = get_latest_acs_year()

    # Compares the newest Census year against the newest year already stored in PostgreSQL.
    new_rent_data = check_for_new_rent_year(
        census_year
    )

    # Checks whether the database already contains the newest Census reporting year.
    if not new_rent_data:

        # Records that no new Census rent dataset needs to be processed.
        logger.info(
            "No new Census rent dataset is currently available."
        )

        # Returns no DataFrame, the current Census year, and False so the pipeline skips transform and load.
        return (
            None,
            census_year,
            False
        )

    # Creates the raw data directory when it does not already exist.
    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Builds the Census ACS API URL for the newest available reporting year.
    api_url = (
        f"https://api.census.gov/data/"
        f"{census_year}/acs/acs5"
    )

    # Defines the parameters required to download state names, median gross rent, and state codes.
    request_parameters = {
        "get": f"NAME,{RENT_VARIABLE}",
        "for": "state:*"
    }

    # Adds the Census API key when one is available.
    if CENSUS_API_KEY:

        # Adds the Census API key to the full dataset request.
        request_parameters[
            "key"
        ] = CENSUS_API_KEY

    # Downloads the complete state-level rent dataset using automatic retries.
    response = get_census_response(
        api_url,
        request_parameters
    )

    # Raises an exception if the complete Census request did not succeed.
    response.raise_for_status()

    # Converts the Census API JSON response into a Python list.
    census_data = response.json()

    # Uses the first Census response row as the DataFrame column names.
    column_names = census_data[
        0
    ]

    # Uses the remaining Census response rows as the dataset records.
    data_rows = census_data[
        1:
    ]

    # Converts the Census response into a Pandas DataFrame.
    rent_dataframe = pd.DataFrame(
        data_rows,
        columns=column_names
    )

    # Saves the raw Census dataset to the project's raw data directory.
    rent_dataframe.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # Records where the raw Census dataset was saved.
    logger.info(
        f"Raw housing data saved to: {OUTPUT_PATH}"
    )

    # Returns the raw DataFrame, reporting year, and True so the pipeline continues to transform and load.
    return (
        rent_dataframe,
        census_year,
        True
    )


# Runs the Census rent extractor only when this file is executed directly.
if __name__ == "__main__":

    # Executes the Census rent extraction process.
    extract_housing_data()

