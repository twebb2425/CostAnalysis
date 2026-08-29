# Imports text so we can execute SQL statements through SQLAlchemy.
from sqlalchemy import text


# Defines a reusable function for loading a DataFrame into PostgreSQL.
def load_dataframe(
    dataframe,
    table_name,
    engine,
    refresh_column=None
):

    # Starts a protected block for the database load operation.
    try:

        # Opens a database transaction that commits automatically if everything succeeds.
        with engine.begin() as connection:

            # Checks whether a refresh column was provided.
            if refresh_column is not None:

                # Gets each unique period contained in the incoming dataset.
                refresh_values = dataframe[refresh_column].dropna().unique()

                # Loops through each period that is about to be loaded.
                for refresh_value in refresh_values:

                    # Creates a parameterized SQL statement that removes only the matching period.
                    delete_query = text(
                        f'DELETE FROM "{table_name}" '
                        f'WHERE "{refresh_column}" = :refresh_value'
                    )

                    # Deletes existing rows for that period without deleting historical periods.
                    connection.execute(
                        delete_query,
                        {"refresh_value": refresh_value.item() if hasattr(refresh_value, "item") else refresh_value}
                    )

            # Loads the DataFrame into the existing PostgreSQL table.
            dataframe.to_sql(

                # Specifies the destination table.
                name=table_name,

                # Uses the current database transaction.
                con=connection,

                # Adds the new rows to the table.
                if_exists="append",

                # Prevents the Pandas index from becoming a PostgreSQL column.
                index=False
            )

        # Returns the number of rows successfully loaded.
        return len(dataframe)

    # Catches any error that occurs during the load.
    except Exception as error:

        # Raises a new error containing information about the failed table.
        raise RuntimeError(
            f"Failed to load data into {table_name}: {error}"
        ) from error