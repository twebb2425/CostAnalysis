# Imports Path so we can build file paths that work across operating systems.
from pathlib import Path

# Imports Pandas for working with the Zillow dataset.
import pandas as pd

# Imports our reusable logging function.
from src.utils.logging_utils import get_logger


# Creates a logger for the state home value transformation module.
logger = get_logger(__name__)


# Finds the root folder of the CostAnalysis project.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Builds the path to the raw Zillow state home value dataset.
RAW_FILE_PATH = PROJECT_ROOT / "data" / "raw" / "home_values_state_raw.csv"

# Builds the path where the processed Zillow dataset will be saved.
PROCESSED_FILE_PATH = PROJECT_ROOT / "data" / "processed" / "home_values_state.csv"


# Defines a reusable function that transforms the raw Zillow state home value dataset.
def transform_home_values_state():

    # Records that the state home value transformation is starting.
    logger.info("Starting state home value transformation.")

    # Loads the raw Zillow dataset into a Pandas DataFrame.
    home_values_df = pd.read_csv(RAW_FILE_PATH)

    # Displays the shape of the raw Zillow dataset for development inspection.
    print("\nRaw Zillow Shape:")
    print(home_values_df.shape)

    # Displays the first five rows of the raw Zillow dataset for development inspection.
    print("\nRaw Zillow Data:")
    print(home_values_df.head())

    # Creates a list containing all Zillow columns that are not monthly date columns.
    identifier_columns = [
        "RegionID",
        "SizeRank",
        "RegionName",
        "RegionType",
        "StateName",
    ]

    # Converts the monthly Zillow columns from wide format into long format.
    home_values_df = home_values_df.melt(
        id_vars=identifier_columns,
        var_name="date",
        value_name="home_value"
    )

    # Renames Zillow columns to match the project's naming convention.
    home_values_df = home_values_df.rename(
        columns={
            "RegionID": "region_id",
            "RegionName": "state_name",
            "RegionType": "geography_type",
        }
    )

    # Converts the Zillow date strings into Pandas datetime values.
    home_values_df["date"] = pd.to_datetime(
        home_values_df["date"],
        format="%Y-%m-%d"
    )

    # Converts the home value column to numeric values while preserving missing values.
    home_values_df["home_value"] = pd.to_numeric(
        home_values_df["home_value"],
        errors="coerce"
    )

    # Capitalizes the geography type so it matches the project's naming style.
    home_values_df["geography_type"] = (
        home_values_df["geography_type"]
        .str.title()
    )

    # Reorders the transformed columns into the final project structure.
    home_values_df = home_values_df[
        [
            "region_id",
            "geography_type",
            "state_name",
            "date",
            "home_value",
        ]
    ]

    # Counts the number of missing Zillow home values.
    missing_home_values = home_values_df["home_value"].isna().sum()

    # Displays the number of missing values for development inspection.
    print("\nMissing Home Values:")
    print(missing_home_values)

    # Displays the first five rows of the transformed dataset.
    print("\nTransformed Zillow Data:")
    print(home_values_df.head())

    # Displays the shape of the transformed dataset.
    print("\nTransformed Zillow Shape:")
    print(home_values_df.shape)

    # Displays the transformed column data types.
    print("\nTransformed Column Data Types:")
    print(home_values_df.dtypes)

    # Saves the transformed Zillow dataset without the Pandas index.
    home_values_df.to_csv(
        PROCESSED_FILE_PATH,
        index=False
    )

    # Records how many rows were created during transformation.
    logger.info(
        f"Transformed {len(home_values_df)} state home value rows."
    )

    # Records how many Zillow values are missing.
    logger.info(
        f"Preserved {missing_home_values} missing home value records."
    )

    # Records where the processed Zillow dataset was saved.
    logger.info(
        f"Processed state home value data saved to: {PROCESSED_FILE_PATH}"
    )

    # Returns the transformed DataFrame so other modules can reuse it.
    return home_values_df


# Runs the transformation only when this file is executed directly.
if __name__ == "__main__":

    # Calls the state home value transformation function.
    transform_home_values_state()