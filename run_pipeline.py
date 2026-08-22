# Import the subprocess module so Python can run other Python scripts.
import subprocess

# Import the sys module so we can use the active virtual environment's Python interpreter.
import sys

# Import the logging module so we can record pipeline activity.
import logging

# Import Path so we can build file paths safely.
from pathlib import Path


# Define the root directory of the project.
PROJECT_ROOT = Path(__file__).resolve().parent

# Define the directory where log files will be stored.
LOG_DIR = PROJECT_ROOT / "logs"

# Create the logs directory if it does not already exist.
LOG_DIR.mkdir(exist_ok=True)

# Define the full path to the pipeline log file.
LOG_FILE = LOG_DIR / "pipeline.log"


# Configure the logging system.
logging.basicConfig(
    # Record informational messages and anything more severe.
    level=logging.INFO,

    # Define how each log entry should appear.
    format="%(asctime)s | %(levelname)s | %(message)s",

    # Send logs to both the log file and the Terminal.
    handlers=[
        # Save log messages to the pipeline log file.
        logging.FileHandler(LOG_FILE),

        # Also display log messages in the Terminal.
        logging.StreamHandler()
    ]
)


# Define a function that runs one step of the pipeline.
def run_step(script_path, step_name):
    # Record that the pipeline step is starting.
    logging.info(f"Starting {step_name} step.")

    # Build the full path to the Python script.
    full_script_path = PROJECT_ROOT / script_path

    # Run the Python script using the active Python interpreter.
    result = subprocess.run(
        # Pass the current Python interpreter and target script.
        [sys.executable, str(full_script_path)],

        # Capture standard output from the script.
        capture_output=True,

        # Capture output as normal text instead of bytes.
        text=True
    )

    # Check whether the script produced normal output.
    if result.stdout:
        # Record the script's normal output.
        logging.info(result.stdout.strip())

    # Check whether the script produced error output.
    if result.stderr:
        # Record the script's error output.
        logging.error(result.stderr.strip())

    # Check whether the script completed successfully.
    if result.returncode == 0:
        # Record that the step completed successfully.
        logging.info(f"{step_name} step completed successfully.")

    # Run this block if the step failed.
    else:
        # Record that the step failed.
        logging.error(f"{step_name} step failed.")

        # Stop the pipeline using the failed script's return code.
        sys.exit(result.returncode)


# Define the main function that controls the pipeline.
def main():
    # Record that the full pipeline is starting.
    logging.info("Starting CostAnalysis data pipeline.")

    # Run the extraction step.
    run_step("src/extract/extract_housing_data.py", "Extract")

    # Run the transformation step.
    run_step("src/transform/transform_housing_data.py", "Transform")

    # Run the database load step.
    run_step("src/load/load_rent_data.py", "Load")

    # Record that the entire pipeline completed successfully.
    logging.info("CostAnalysis data pipeline completed successfully.")


# Check whether this script is being executed directly.
if __name__ == "__main__":
    # Run the main pipeline function.
    main()