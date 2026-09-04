# CostAnalysis

An end-to-end data engineering project that collects, transforms, validates, and stores U.S. housing cost data using automated ETL pipelines, cloud PostgreSQL, and GitHub Actions.

## Project Overview

CostAnalysis was built to explore the engineering side of working with continuously updated public datasets.

The project currently integrates two housing-related datasets:

- U.S. Census ACS Median Gross Rent
- Zillow Home Value Index (ZHVI)

Rather than simply downloading and analyzing static CSV files, the project is designed as an automated data pipeline that checks source freshness, determines whether new data has been released, and only performs transformation and loading when an update is required.

The production database is hosted in Supabase PostgreSQL, while GitHub Actions handles scheduled execution of the pipeline.

## Architecture

```mermaid
flowchart TD

    A[Census ACS API] --> C[Python Extract Layer]
    B[Zillow Research Data] --> C

    C --> D[Freshness Checks]

    D -->|No New Data| E[Skip Processing]
    D -->|New Data Available| F[Transform]

    F --> G[Validation]
    G --> H[Load]

    H --> I[Supabase PostgreSQL]

    J[GitHub Actions] --> C

Pipeline Workflow
Connect to the external data source.
Identify the most recent reporting period available.
Query PostgreSQL for the latest reporting period already stored.
Compare the source and database.
Skip processing when the database is current.
Extract the complete dataset when new data is detected.
Transform the source data into a standardized structure.
Validate the transformed data.
Load the records into PostgreSQL.
Log pipeline activity for troubleshooting and monitoring.

Data Sources
U.S. Census ACS
The Census pipeline retrieves state-level Median Gross Rent from the American Community Survey 5-Year dataset.
Current database reporting year:
2024
52 state-level records

Zillow Home Value Index
The Zillow pipeline retrieves monthly state-level home value data from the Zillow Home Value Index.
Current database coverage:
January 2000 through July 2026
16,269 records
State-level monthly observations

Technology Stack
Programming
Python 3.13
Pandas
Requests
SQLAlchemy
Psycopg
python-dotenv
Data Storage
PostgreSQL
Supabase
DevOps / Automation
Git
GitHub
GitHub Actions
Scheduled workflow execution
Repository Secrets
Data Engineering Concepts
ETL pipelines
Data extraction
Data transformation
Data validation
Incremental loading
Data freshness detection
Cloud databases
Environment variables
CI/CD
Logging
Retry handling
Modular Python architecture

CostAnalysis/
├── .github/
│   └── workflows/
│       └── cost_analysis_pipeline.yml
├── data/
│   ├── raw/
│   └── processed/
├── logs/
├── src/
│   ├── extract/
│   │   ├── extract_rent.py
│   │   └── extract_home_values_state.py
│   ├── transform/
│   │   ├── transform_rent.py
│   │   └── transform_home_values_state.py
│   ├── load/
│   │   ├── load_rent.py
│   │   └── load_home_values_state.py
│   └── utils/
│       ├── database.py
│       ├── freshness.py
│       ├── loader.py
│       ├── logging_utils.py
│       └── validation.py
├── migrate_to_supabase.py
├── requirements.txt
├── run_pipeline.py
└── README.md

Cloud Database
The production database is hosted using Supabase PostgreSQL.
Database credentials are never stored directly in the repository. Connection information and API credentials are supplied through environment variables locally and GitHub Repository Secrets in the CI/CD environment.
The primary production tables are:
housing_costs
home_values_state
Automated Freshness Checks
A major goal of this project was avoiding unnecessary processing.
Before performing transformation or loading, the pipeline compares the newest reporting period from each source against the newest value stored in PostgreSQL.
Example:
Latest Zillow source date: 2026-07-31
Latest PostgreSQL date:    2026-07-31

Result:
No new Zillow month detected.
Transform and load skipped.
When a future dataset is released, the pipeline will automatically continue through the transformation, validation, and loading stages.
Reliability
External APIs are not always immediately available.
The Census extraction layer includes retry handling and increased request timeouts so temporary network or API issues do not immediately terminate the automated pipeline.
The pipeline also creates required directories dynamically, allowing it to run successfully inside temporary GitHub Actions environments.
CI/CD
GitHub Actions executes the complete pipeline automatically on a scheduled basis.
The workflow:
Creates a clean Ubuntu environment.
Checks out the repository.
Installs Python.
Installs project dependencies.
Loads secured environment variables.
Executes the complete ETL pipeline.
Connects to the Supabase PostgreSQL database.
Processes new data when available.
The workflow can also be manually triggered through GitHub Actions.
Running Locally
Create and activate a Python virtual environment.
Install dependencies:
pip install -r requirements.txt
Create a local .env file containing the required environment variables.
CENSUS_API_KEY=
DATABASE_URL=
Run the complete pipeline:
python run_pipeline.py
What I Learned
This project began as a basic housing-cost analysis and evolved into an end-to-end data engineering pipeline.
Key areas explored while building the project included:
Designing modular ETL architecture
Working with multiple external data sources
Building reusable database utilities
Managing PostgreSQL from Python
Implementing incremental data loading
Detecting source-data freshness
Moving a database workload from local PostgreSQL to cloud PostgreSQL
Managing application secrets
Creating scheduled CI/CD workflows
Debugging differences between local and cloud execution environments
Handling unreliable external APIs
Future Improvements
Potential future enhancements include:
Additional cost-of-living datasets
Fuel price data
City and ZIP-code level analysis
Data quality testing
Pipeline notifications
Automated analytics dashboards
Cloud-native deployment
Additional CI/CD testing
