# Imports Python's built-in operating system tools for accessing environment variables.
import os

# Imports the current date so we can determine which Census years to check.
from datetime import datetime

# Imports Path so we can build file paths that work across operating systems.
from pathlib import Path

# Imports Pandas for creating and working with DataFrames.
import pandas as pd

# Imports requests so Python can send HTTP requests to the Census API.
import requests

# Imports our reusable logging function.
from src.utils.logging_utils import get_logger

# Imports our reusable Census freshness check function.
from src.utils.freshness import check_for_new_rent_year

# Imports dotenv so Python can read variables stored in the .env file.
from dotenv import load_dotenv


# Creates a logger for the housing data extraction module.
logger = get_logger(__name__)


# Loads variables stored in the project's .env file.
load_dotenv()


# Retrieves the Census API key from the environment variables.
API_KEY = os.getenv("CENSUS_API_KEY")


# Finds the root folder of the CostAnalysis project.
PROJECT_ROOT = Path(__file__).resolve().parents[2]


# Builds the full path where the raw Census rent dataset will be saved.
OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "housing_costs_raw.csv"


# Defines a reusable function that finds the newest available ACS 5-year dataset.
def get_latest_acs_year():

    # Gets the current calendar year.
    current_year = datetime.now().year

    # Checks the current year and several previous years for an available ACS dataset.
    for year in range(current_year, current_year - 5, -1):

        # Builds the Census ACS 5-year API URL for the year being checked.
        api_url = f"https://api.census.gov/data/{year}/acs/acs5"

        # Creates simple parameters used only to test whether the dataset exists.
        test_parameters = {

            # Requests only the geography name for the availability test.
            "get": "NAME",

            # Requests every state-level geography.
            "for": "state:*",

            # Sends the Census API key with the request.
            "key": API_KEY,
        }

        # Sends a request to check whether this Census dataset is available.
        response = requests.get(
            api_url,
            params=test_parameters,
            timeout=30
        )

        # Checks whether the Census API returned a successful response.
        if response.status_code == 200:

            # Returns the first year that successfully responds.
            return year

    # Stops the program if no ACS dataset was found in the years checked.
    raise RuntimeError(
        "No recent ACS 5-year dataset could be found."
    )


# Defines a reusable function that extracts state-level rent data from the Census API.
def extract_housing_data():

    # Finds the newest available ACS 5-year Census year.
    census_year = get_latest_acs_year()

    # Records which ACS dataset year was selected.
    logger.info(
        f"Latest ACS 5-year dataset found: {census_year}"
    )

    # Compares the newest Census source year against the newest year in PostgreSQL.
    new_rent_data = check_for_new_rent_year(
        census_year
    )

    # Checks whether Census has published a newer ACS year.
    if not new_rent_data:

        # Records that no newer Census rent dataset is currently available.
        logger.info(
            "No new Census rent dataset is currently available."
        )

        # Returns no DataFrame, the detected Census year, and False for freshness.
        return None, census_year, False

    # Records that a newer Census rent dataset is available.
    logger.info(
        "A new Census rent dataset is available for processing."
    )

    # Builds the Census API URL using the newest available year.
    api_url = f"https://api.census.gov/data/{census_year}/acs/acs5"

    # Creates the parameters that will be sent to the Census API.
    census_parameters = {

        # Requests the state name and median gross rent.
        "get": "NAME,B25064_001E",

        # Requests data for every state-level geography.
        "for": "state:*",

        # Sends the Census API key with the request.
        "key": API_KEY,
    }

    # Sends the request to the Census API.
    response = requests.get(
        api_url,
        params=census_parameters,
        timeout=30
    )

    # Raises an error if the Census API returns an unsuccessful response.
    response.raise_for_status()

    # Converts the JSON response into a Python data structure.
    data = response.json()

    # Stores the first returned row as the DataFrame column names.
    columns = data[0]

    # Stores all remaining returned rows as the observations.
    rows = data[1:]

    # Converts the Census observations into a Pandas DataFrame.
    rent_df = pd.DataFrame(
        rows,
        columns=columns
    )

    # Displays the first five rows of the extracted dataset.
    print(
        rent_df.head()
    )

    # Saves the raw Census dataset without the Pandas index.
    rent_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # Records where the raw housing dataset was saved.
    logger.info(
        f"Raw housing data saved to: {OUTPUT_PATH}"
    )

    # Returns the DataFrame, Census year, and True so the pipeline continues.
    return rent_df, census_year, True


# Runs the extraction only when this file is executed directly.
if __name__ == "__main__":

    # Calls the reusable Census housing data extraction function.
    extract_housing_data()

