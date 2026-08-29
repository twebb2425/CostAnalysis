# Imports the reusable rent extraction function.
from src.extract.extract_rent import extract_housing_data

# Imports the reusable rent transformation function.
from src.transform.transform_rent import transform_housing_data

# Imports the reusable rent loading function.
from src.load.load_rent import load_rent_data

# Imports the reusable Zillow state home value extraction function.
from src.extract.extract_home_values_state import extract_home_values_state

# Imports the reusable Zillow state home value transformation function.
from src.transform.transform_home_values_state import transform_home_values_state

# Imports the reusable Zillow state home value loading function.
from src.load.load_home_values_state import load_home_values_state

# Imports our reusable logging function.
from src.utils.logging_utils import get_logger


# Creates a logger for the main CostAnalysis pipeline.
logger = get_logger(__name__)


# Defines the reusable rent ETL pipeline.
def run_rent_pipeline():

    # Records that the rent ETL pipeline is starting.
    logger.info("Starting rent ETL pipeline.")

    # Extracts the latest available Census rent data and returns its Census year.
    _, census_year = extract_housing_data()

    # Transforms the raw rent data using the Census year detected during extraction.
    transform_housing_data(census_year)

    # Loads the processed rent data into PostgreSQL.
    load_rent_data()

    # Records that the rent ETL pipeline completed successfully.
    logger.info("Rent ETL pipeline completed successfully.")


# Defines the reusable state home value ETL pipeline.
def run_home_values_pipeline():

    # Records that the Zillow state home value ETL pipeline is starting.
    logger.info("Starting state home value ETL pipeline.")

    # Downloads the latest Zillow state home value dataset and checks its freshness.
    extract_home_values_state()

    # Transforms the raw Zillow state home value dataset into long format.
    transform_home_values_state()

    # Loads the transformed Zillow state home values into PostgreSQL using an upsert.
    load_home_values_state()

    # Records that the Zillow state home value ETL pipeline completed successfully.
    logger.info("State home value ETL pipeline completed successfully.")


# Defines the main CostAnalysis pipeline that runs every dataset.
def run_pipeline():

    # Records that the complete CostAnalysis pipeline is starting.
    logger.info("Starting complete CostAnalysis ETL pipeline.")

    # Starts a protected block for the complete ETL workflow.
    try:

        # Runs the Census rent ETL pipeline.
        run_rent_pipeline()

        # Runs the Zillow state home value ETL pipeline.
        run_home_values_pipeline()

        # Records that every CostAnalysis ETL pipeline completed successfully.
        logger.info(
            "Complete CostAnalysis ETL pipeline completed successfully."
        )

    # Catches any error that occurs anywhere in the complete pipeline.
    except Exception as error:

        # Records the full error and traceback in the terminal and log file.
        logger.exception(
            f"CostAnalysis ETL pipeline failed: {error}"
        )

        # Raises the error again so automated systems can detect the failure.
        raise


# Runs the complete pipeline only when this file is executed directly.
if __name__ == "__main__":

    # Calls the main CostAnalysis pipeline function.
    run_pipeline()