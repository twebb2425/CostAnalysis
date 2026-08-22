#Import Python built in OS tools for access to enviroment variables
import os

import pandas as pd

# Import path so we can build file paths that work across OS
from pathlib import Path

#Allows Python send HTTP requests to APIs
import requests

# Import dotenv libray so Python can read variables stored in .env files
from dotenv import load_dotenv

# Load varibales stored in the .env folder
load_dotenv()

#Create variable that retrives the API key
API_KEY = os.getenv("CENSUS_API_KEY")

"""
Create if-else statement that states if the key was pulled correctly for testing first
if API_KEY:
    print("Key found sucessfully.")
else:
    print("Key not found.")
"""

# Store the API Key Website
API_URL = "https://api.census.gov/data/2024/acs/acs5"

# Create Dictionary with the parameters that will be sent to the API
CENSUS_PARAMETERS = {
    # Request the state name and median rent
    "get": "NAME,B25064_001E",
    # Gather data for all state level geograpghy
    "for": "state:*",
    # Sends the key with the request
    "key": API_KEY,
}
# Create reponse variable that sends the get request and has a timeout function
RESPONSE = requests.get(API_URL, params=CENSUS_PARAMETERS, timeout=30)

# Raises an error if the gets an unsucessfull HTTP reponse
RESPONSE.raise_for_status()

# Convert the JSON reponse from the API into data structure
data = RESPONSE.json()

#Take the first row returned by the API and store it as column names
columns = data[0]

#Take all rows after the first one and store it as our observational data
rows = data[1:]

# Convert observations to dataframe
rent_df = pd.DataFrame(rows, columns=columns)

# display the first 5 rows
print(rent_df.head())

# Find root folder of the folder of project
PROJECT_ROOT = Path(__file__).resolve().parents[2] 

# Builds full path to the raw dataset
OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "housing_costs_raw.csv"

# Saves the dataframe as a csv without the pandas index
rent_df.to_csv(OUTPUT_PATH, index=False) 

# displays the location where the file was saved
print("Raw housing data saved to:", OUTPUT_PATH)

