# Imports Path so we can build file paths that work across operating systems.
from pathlib import Path

# Imports the Pandas library for working with tabular data.
import pandas as pd

# Imports our reusable logging function.
from src.utils.logging_utils import get_logger

# Creates a logger for the housing data transformation module.
logger = get_logger(__name__)

# Finds the project root because this file is two folders below the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Builds the full path to the raw housing cost CSV file.
RAW_FILE_PATH = PROJECT_ROOT / "data" / "raw" / "housing_costs_raw.csv"

# Builds the full path to the processed housing cost CSV file.
PROCESSED_FILE_PATH = PROJECT_ROOT / "data" / "processed" / "housing_costs.csv"


# Defines a reusable function that transforms the raw rent dataset.
def transform_housing_data(census_year):

    # Loads the raw rent data into a Pandas DataFrame.
    rent_df = pd.read_csv(RAW_FILE_PATH)

    # Displays the first five rows of the raw dataset.
    print(rent_df.head())

    # Displays the number of rows and columns in the raw dataset.
    print("\nDataFrame Shape:")
    print(rent_df.shape)

    # Displays the data type of each raw column.
    print("\nColumn Data Types:")
    print(rent_df.dtypes)

    # Displays the number of missing values in each column.
    print("\nMissing Values by Column:")
    print(rent_df.isna().sum())

    # Displays the number of duplicate rows in the raw dataset.
    print("\nDuplicate Rows:")
    print(rent_df.duplicated().sum())

    # Renames the Census columns to clearer names used throughout the project.
    rent_df = rent_df.rename(
        columns={
            "NAME": "state_name",
            "B25064_001E": "median_gross_rent",
            "state": "state_code"
        }
    )

    # Converts the state code to a string and pads single-digit codes with a leading zero.
    rent_df["state_code"] = rent_df["state_code"].astype(str).str.zfill(2)

    # Adds the Census observation year that was detected during extraction.
    rent_df["year"] = census_year

    # Adds the geographic level represented by each row.
    rent_df["geography_type"] = "State"

    # Reorders the columns into the standard format used by the project.
    rent_df = rent_df[
        [
            "geography_type",
            "state_name",
            "state_code",
            "year",
            "median_gross_rent",
        ]
    ]

    # Displays the first five rows of the cleaned dataset.
    print("\nCleaned Rent Data:")
    print(rent_df.head())

    # Displays the data type of each cleaned column.
    print("\nCleaned Column Data Types:")
    print(rent_df.dtypes)

    # Saves the cleaned dataset without the Pandas index.
    rent_df.to_csv(PROCESSED_FILE_PATH, index=False)

    # Records where the processed housing dataset was saved.
    logger.info(f"Processed data saved to: {PROCESSED_FILE_PATH}")

    # Returns the transformed DataFrame so other Python modules can reuse it later.
    return rent_df


# Runs the transformation only when this file is executed directly.
if __name__ == "__main__":

    # Uses 2024 only when manually testing the transform script by itself.
    test_census_year = 2024

    # Calls the reusable housing data transformation function.
    transform_housing_data(test_census_year)
