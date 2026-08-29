# Defines a reusable function that validates a Pandas DataFrame before loading.
def validate_dataframe(dataframe, required_columns):

    # Checks whether any required columns are missing from the DataFrame.
    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    # Stops the program if any required columns are missing.
    if missing_columns:

        # Raises an error that identifies which required columns are missing.
        raise ValueError(f"Missing required columns: {missing_columns}")

    # Checks whether the DataFrame contains zero rows.
    if dataframe.empty:

        # Stops the program instead of allowing an empty dataset to continue.
        raise ValueError("The dataset is empty.")

    # Returns the number of validated rows so the calling script can report it.
    return len(dataframe)