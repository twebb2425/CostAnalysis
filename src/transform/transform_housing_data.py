# import Path library to build file paths that work across OS systems
from pathlib import Path

import pandas as pd

# finds the top level level since we are 2 levels down
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Build the full path to the raw csv file
RAW_FILE_PATH = PROJECT_ROOT / "data" / "raw" / "housing_costs_raw.csv"

# load the rent data into a dataframe
rent_df = pd.read_csv(RAW_FILE_PATH)

"""
This section of code is for validation checks to ensure file path is uploaded, check for column values, and inspect the raw data
"""

# display the first 5 rows using .head()
print(rent_df.head())

# display the shape of the dataframe
print("\nDataFrame Shape:")
print(rent_df.shape)

# show the column types
print("\nColumn data types:")
print(rent_df.dtypes)

#find the missing values
print("\nMissing values by column:")
print(rent_df.isna().sum())

# find duplicate rows
print("\nDuplicate Rows:")
print(rent_df.duplicated().sum())

"""
This section of code transforms column names, values, and adds columns as needed
"""

# Use the rename function to change the column names for clarity
rent_df = rent_df.rename(
    columns={
        "NAME": "state_name",
        "B25064_001E": "median_gross_rent",
        "state": "state_code"
    }
)

# Convert State Code to String to keep values like 1 as 01
rent_df["state_code"] = rent_df["state_code"].astype(str).str.zfill(2)

# Add the Census year observation
rent_df["year"] = 2024

# Add column that shares the geopraphy type
rent_df["geography_type"] = "State"

# Reorder the columns into consistent format
rent_df = rent_df[
    [# Start the list
    "geography_type",
    "state_name",
    "state_code",
    "year",
    "median_gross_rent",
    ]
]

"""
More Validation checks to ensure data types were changed accordingly and our data displays correctly
"""

# display the first 5 rows
print("\nCleaned Rent Data:")
print(rent_df.head())

# display column types
print("\nCleaned Column Data Types:")
print(rent_df.dtypes)

# create a processed file path
PROCESSED_FILE_PATH = PROJECT_ROOT / "data" / "processed" / "housing_costs.csv"

# Save the new file without the pandas index values
rent_df.to_csv(PROCESSED_FILE_PATH, index=False)

# Display verification where the file was saved
print("Processed data saved to:", PROCESSED_FILE_PATH)