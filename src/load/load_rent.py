# Import pandas library.
import pandas as pd

# Imports our reusable PostgreSQL database connection function.
from src.utils.database import get_database_engine

# Imports our reusable PostgreSQL DataFrame loading function.
from src.utils.loader import load_dataframe

# Imports our reusable DataFrame validation function.
from src.utils.validation import validate_dataframe

# Imports our reusable logging function.
from src.utils.logging_utils import get_logger


# Creates a logger for the rent data loading module.
logger = get_logger(__name__)


# Defines a reusable function that loads processed rent data into PostgreSQL.
def load_rent_data():

    # Creates the PostgreSQL database connection using our reusable database utility.
    engine = get_database_engine()

    # Stores the processed housing cost file path.
    processed_file = "data/processed/housing_costs.csv"

    # Reads the processed housing cost CSV into a Pandas DataFrame.
    rent_data = pd.read_csv(
        processed_file,
        dtype={"state_code": str}
    )

    # Creates a list of columns required for the rent dataset.
    expected_columns = [
        "geography_type",
        "state_name",
        "state_code",
        "year",
        "median_gross_rent",
    ]

    # Validates the rent DataFrame using our shared validation utility.
    validated_rows = validate_dataframe(
        dataframe=rent_data,
        required_columns=expected_columns
    )

    # Records how many rows passed validation.
    logger.info(f"Validated {validated_rows} rows for loading.")

    # Displays the first five rows of the validated dataset.
    print(rent_data.head())

    # Loads the validated rent data while preserving data from previous years.
    loaded_rows = load_dataframe(
        dataframe=rent_data,
        table_name="housing_costs",
        engine=engine,
        refresh_column="year"
    )

    # Records how many rows were successfully loaded into PostgreSQL.
    logger.info(f"Successfully loaded {loaded_rows} rows into housing_costs.")


# Runs the rent loader only when this file is executed directly.
if __name__ == "__main__":

    # Calls the reusable rent loading function.
    load_rent_data()

"""
print(f"Housing cost data successfully loaded into PostgreSQL")
"""