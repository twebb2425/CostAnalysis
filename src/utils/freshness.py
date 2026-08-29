# Imports Pandas so we can work with date values.
import pandas as pd

# Imports SQLAlchemy text so we can safely execute SQL queries.
from sqlalchemy import text

# Imports our reusable database connection function.
from src.utils.database import get_database_engine

# Imports our reusable logging function.
from src.utils.logging_utils import get_logger


# Creates a logger for the freshness utility module.
logger = get_logger(__name__)


# Defines a reusable function that checks the newest date currently stored in PostgreSQL.
def get_latest_database_date():

    # Creates the PostgreSQL database engine.
    engine = get_database_engine()

    # Opens a connection to PostgreSQL.
    with engine.connect() as connection:

        # Queries the newest home value date currently stored in the database.
        result = connection.execute(
            text(
                """
                SELECT MAX(date)
                FROM home_values_state
                """
            )
        )

        # Retrieves the single date value returned by PostgreSQL.
        latest_database_date = result.scalar()

    # Returns None if the table does not contain any dates yet.
    if latest_database_date is None:

        # Records that no previous home value data exists.
        logger.info(
            "No existing home value date was found in PostgreSQL."
        )

        # Returns None so the caller knows this is the first load.
        return None

    # Converts the PostgreSQL date into a Pandas Timestamp for easier comparison.
    latest_database_date = pd.Timestamp(
        latest_database_date
    )

    # Records the latest date currently stored in PostgreSQL.
    logger.info(
        f"Latest home value date currently in PostgreSQL: {latest_database_date.date()}."
    )

    # Returns the latest database date.
    return latest_database_date


# Defines a reusable function that compares the source date against the database date.
def check_for_new_home_value_month(
    latest_source_date
):

    # Converts the source date into a Pandas Timestamp.
    latest_source_date = pd.Timestamp(
        latest_source_date
    )

    # Gets the newest date currently stored in PostgreSQL.
    latest_database_date = get_latest_database_date()

    # Checks whether the database is currently empty.
    if latest_database_date is None:

        # Records that this is effectively the first database load.
        logger.info(
            f"Initial home value load detected. Source latest date: {latest_source_date.date()}."
        )

        # Returns True because all source data is new to the database.
        return True

    # Checks whether the Zillow source contains a newer month than PostgreSQL.
    if latest_source_date > latest_database_date:

        # Records that Zillow has published a newer month.
        logger.info(
            f"New Zillow home value month detected: "
            f"{latest_database_date.date()} -> {latest_source_date.date()}."
        )

        # Returns True because a newer reporting month exists.
        return True

    # Checks whether Zillow and PostgreSQL currently have the same newest month.
    if latest_source_date == latest_database_date:

        # Records that no newer reporting month has been published yet.
        logger.info(
            f"No new Zillow month detected. "
            f"Source and database both end at {latest_source_date.date()}."
        )

        # Returns False because there is no newer month.
        return False

    # Records a warning if the source somehow contains older data than our database.
    logger.warning(
        f"Zillow source appears older than PostgreSQL. "
        f"Source: {latest_source_date.date()} | "
        f"Database: {latest_database_date.date()}."
    )

    # Returns False because the source does not contain a newer month.
    return False