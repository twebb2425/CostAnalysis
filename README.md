# CostAnalysis

CostAnalysis is a housing data project I built to get hands-on experience with ETL pipelines, PostgreSQL, cloud databases, and workflow automation.

The project pulls state-level housing data from the U.S. Census Bureau and Zillow, processes it with Python, stores it in a Supabase PostgreSQL database, and uses the data in a Streamlit dashboard.

## Live Dashboard

View the dashboard here:(https://costanalysis-app.streamlit.app)

## What It Does

The project currently uses two datasets:

- U.S. Census ACS Median Gross Rent
- Zillow Home Value Index (ZHVI)

The Census data provides annual state-level median rent data, while Zillow provides monthly home value data going back to 2000.

Instead of downloading the data manually each time it changes, I built the pipeline to check whether a newer reporting period is available before processing anything.

If the database already contains the latest data, the pipeline skips the update. If new data is available, it extracts, transforms, validates, and loads the new dataset into PostgreSQL.

## How It Works

The basic flow is:

Census ACS / Zillow  
↓  
Python extraction  
↓  
Freshness check  
↓  
Transformation and validation  
↓  
Supabase PostgreSQL  
↓  
Streamlit dashboard

GitHub Actions is used to run the pipeline on a schedule, and it can also be triggered manually.

## Dashboard

I built a Streamlit dashboard on top of the PostgreSQL data to make the results easier to explore.

The dashboard allows users to select a state and view:

- Median gross rent
- Latest Zillow home value
- Home value change since 2015
- Home value history since 2015
- National home value ranking
- Comparison with other states

The dashboard queries the cloud database rather than reading directly from the project's CSV files.

## Data

### Census ACS

The rent pipeline uses the American Community Survey 5-Year dataset and retrieves state-level Median Gross Rent.

Current data:

- 2024 reporting year
- 52 state-level records

### Zillow

The home value pipeline uses Zillow's Home Value Index.

Current data:

- January 2000 through July 2026
- 16,269 monthly state-level records

## Tech Used

- Python
- Pandas
- SQLAlchemy
- Psycopg
- PostgreSQL
- Supabase
- Streamlit
- Altair
- Git / GitHub
- GitHub Actions
- Census API
- Zillow Research Data

## Running the Project

Install the required packages:

```bash
pip install -r requirements.txt
```

Create a `.env` file containing:

```text
CENSUS_API_KEY=
DATABASE_URL=
```

Run the full ETL pipeline:

```bash
python run_pipeline.py
```

Run the dashboard:

```bash
streamlit run app.py
```

## What I Took Away From It

This project started as a simple idea for comparing housing costs. I ended up using it as a way to learn more about the engineering work that happens before data reaches a dashboard or analysis.

The biggest thing I learned was how many pieces have to work together outside of the actual analysis. I worked through API extraction, data cleaning, validation, PostgreSQL loading, environment variables, cloud database connections, GitHub Actions, logging, and problems that only appeared once the code was running outside my local environment.

AI was used throughout the project as a development and learning tool, particularly when I was working through unfamiliar data engineering concepts and debugging issues. I tried to use the project to understand why each part of the pipeline worked rather than treating generated code as a finished product.

This was my first attempt at building a complete automated data pipeline from source data through a cloud database and into a usable dashboard.