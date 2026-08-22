# Import the OS
import os

# Import function that loads variables from .env file
from dotenv import load_dotenv

# Import pandas library
import pandas as pd

# Import the SQLAlchemy function
from sqlalchemy import create_engine, text

# load the databse settings stored in the .env file
load_dotenv()

# Get database host
db_host = os.getenv("DB_HOST")

# Get the database port
db_port = os.getenv("DB_PORT")

# Get the database name from .env
db_name = os.getenv("DB_NAME")

# Get the database username
db_user = os.getenv("DB_USER")

# Get the database password
db_password = os.getenv("DB_PASSWORD")

# Create database URL 
database_url = f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Create the sqlachemy engine that python will use to communicate with PostgreSQL
engine = create_engine(database_url)

# Run try and exception to connect to the database
try:
    with engine.connect() as connection:
        print("Successfully connected to PostgreSQL")
except Exception as error: 
    print("Databade connection failed", error)

# Store the processed file as variable
processed_file = "data/processed/housing_costs.csv"

# Read file into pandas dataframe
rent_data = pd.read_csv(processed_file)

# Creates a list of columns that must exist before we load the data into PostgreSQL.
expected_columns = [ 
    "geography_type",  

    "state_name",  

    "state_code",  

    "year",  

    "median_gross_rent",

]  

# Checks whether any required columns are missing from the DataFrame.
missing_columns = [column for column in expected_columns if column not in rent_data.columns] 

# Checks whether the missing-columns list contains anything.
if missing_columns: 
    # Stops the program and identifies the missing columns.
    raise ValueError(f"Missing required columns: {missing_columns}")  

# Checks whether the processed dataset contains zero rows.
if rent_data.empty:  

    # Stops the program instead of loading an empty dataset.
    raise ValueError("The processed housing cost dataset is empty.")

# Displays the number of rows that passed validation.
print(f"Validated {len(rent_data)} rows for loading.") 

# Display the first 5 rows
print(rent_data.head())

# Starts a protected block for the database load operation.
try:  
    # Opens a database transaction that automatically commits if everything succeeds.
    with engine.begin() as connection: 
        # Removes the previous housing data while keeping the existing PostgreSQL table.
        connection.execute(text("DELETE FROM housing_costs"))  

        # Sends the validated Pandas DataFrame into PostgreSQL.
        rent_data.to_sql(  
            
            # Specifies the PostgreSQL table that will receive the data.
            name="housing_costs", 

            # Uses the active SQLAlchemy transaction for the load.
            con=connection, 

            # Adds rows to the existing table instead of deleting and recreating the table itself.
            if_exists="append", 

            # Prevents the Pandas DataFrame index from becoming an unnecessary SQL column.
            index=False 

        ) 


    print(f"Successfully loaded {len(rent_data)} rows into housing_costs.")  # Reports how many rows were successfully loaded.


except Exception as error:  # Catches any error that occurs during the PostgreSQL load.

    print(f"Data load failed: {error}")  # Displays the database error so we can troubleshoot it.

"""
print(f"Housing cost data successfully loaded into PostgreSQL")
"""