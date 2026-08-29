# Imports Python's built-in logging library.
import logging

# Imports Path so we can create a log file path that works across operating systems.
from pathlib import Path


# Finds the root folder of the CostAnalysis project.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Creates the folder path where log files will be stored.
LOG_DIRECTORY = PROJECT_ROOT / "logs"

# Creates the logs folder if it does not already exist.
LOG_DIRECTORY.mkdir(exist_ok=True)

# Creates the full path for the main pipeline log file.
LOG_FILE_PATH = LOG_DIRECTORY / "cost_analysis.log"


# Defines a reusable function that creates a logger for the project.
def get_logger(logger_name):

    # Creates or retrieves a logger with the provided name.
    logger = logging.getLogger(logger_name)

    # Sets the minimum logging level to INFO.
    logger.setLevel(logging.INFO)

    # Checks whether handlers have already been added to prevent duplicate log messages.
    if not logger.handlers:

        # Creates the format used for each log message.
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        # Creates a handler that displays log messages in the terminal.
        console_handler = logging.StreamHandler()

        # Applies the shared log format to terminal messages.
        console_handler.setFormatter(formatter)

        # Creates a handler that writes log messages to the project log file.
        file_handler = logging.FileHandler(LOG_FILE_PATH)

        # Applies the shared log format to file messages.
        file_handler.setFormatter(formatter)

        # Adds the terminal handler to the logger.
        logger.addHandler(console_handler)

        # Adds the file handler to the logger.
        logger.addHandler(file_handler)

    # Returns the configured logger so other modules can reuse it.
    return logger