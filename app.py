# Imports Streamlit for the dashboard.
import streamlit as st

# Imports Pandas for working with tabular data.
import pandas as pd

# Imports Altair for interactive charts.
import altair as alt

# Imports SQLAlchemy for database connections and SQL queries.
from sqlalchemy import create_engine, text

# Imports os for reading environment variables.
import os

# Imports dotenv so we can load the local .env file.
from dotenv import load_dotenv


# Loads environment variables from the .env file.
load_dotenv(".env")

# Reads the PostgreSQL connection string from the environment.
database_url = os.getenv("DATABASE_URL")

# Converts the PostgreSQL URL so SQLAlchemy uses Psycopg 3.
if database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )

# Creates the database engine.
engine = create_engine(database_url)


# Sets the Streamlit page configuration.
st.set_page_config(
    page_title="Cost Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)


# Displays the dashboard title.
st.title("Cost Analysis Dashboard")

# Displays a short description under the title.
st.write(
    "Explore state-level rent and home value trends using data "
    "from the U.S. Census Bureau and Zillow."
)


# Defines the rent query.
rent_query = text("""
    SELECT
        state_name,
        year,
        median_gross_rent
    FROM housing_costs
    ORDER BY state_name;
""")

# Loads rent data from PostgreSQL into a Pandas DataFrame.
rent_df = pd.read_sql(
    rent_query,
    engine
)


# Defines the home value query.
home_value_query = text("""
    SELECT
        state_name,
        date,
        home_value
    FROM home_values_state
    ORDER BY state_name, date;
""")

# Loads home value data from PostgreSQL into a Pandas DataFrame.
home_df = pd.read_sql(
    home_value_query,
    engine
)


# Converts the home value date column into datetime format.
home_df["date"] = pd.to_datetime(
    home_df["date"]
)


# Creates a sorted list of states that exist in both datasets.
states = sorted(
    set(rent_df["state_name"]).intersection(
        set(home_df["state_name"])
    )
)


# Finds the default dropdown index for North Carolina.
default_state_index = (
    states.index("North Carolina")
    if "North Carolina" in states
    else 0
)


# Creates the state dropdown.
selected_state = st.selectbox(
    "Select a state",
    states,
    index=default_state_index
)


# Filters the rent dataset to the selected state.
selected_rent = rent_df[
    rent_df["state_name"] == selected_state
].copy()


# Filters the home value dataset to the selected state.
selected_home = home_df[
    home_df["state_name"] == selected_state
].copy()


# Sorts rent records by year.
selected_rent = selected_rent.sort_values(
    "year"
)


# Sorts home value records by date.
selected_home = selected_home.sort_values(
    "date"
)


# Gets the latest rent record.
latest_rent_row = selected_rent.iloc[-1]


# Gets the latest rent value.
latest_rent = latest_rent_row[
    "median_gross_rent"
]


# Gets the year associated with the latest rent value.
latest_rent_year = latest_rent_row[
    "year"
]


# Gets the latest home value record.
latest_home_row = selected_home.iloc[-1]


# Gets the latest home value.
latest_home_value = latest_home_row[
    "home_value"
]


# Gets the date associated with the latest home value.
latest_home_date = latest_home_row[
    "date"
]


# Finds the first home value record from 2015 or later.
home_2015_row = selected_home[
    selected_home["date"].dt.year >= 2015
].iloc[0]


# Gets the starting home value used for the comparison.
home_2015_value = home_2015_row[
    "home_value"
]


# Calculates the percentage change in home value since 2015.
home_value_change_pct = (
    (
        latest_home_value
        - home_2015_value
    )
    / home_2015_value
) * 100


# Creates three KPI columns.
col1, col2, col3 = st.columns(3)


# Displays the median gross rent KPI.
with col1:
    st.metric(
        label=f"Median Gross Rent ({latest_rent_year})",
        value=f"${latest_rent:,.0f}"
    )


# Displays the latest home value KPI.
with col2:
    st.metric(
        label=f"Typical Home Value ({latest_home_date:%b %Y})",
        value=f"${latest_home_value:,.0f}"
    )


# Displays the percentage change in home value since 2015.
with col3:
    st.metric(
        label="Home Value Change Since 2015",
        value=f"{home_value_change_pct:+.1f}%"
    )


# Adds the home value trend section.
st.subheader(
    f"Home Value Trend — {selected_state}"
)


# Limits the chart to 2015 and later.
chart_df = selected_home[
    selected_home["date"].dt.year >= 2015
].copy()


# Finds the lowest home value in the displayed period.
y_min = chart_df[
    "home_value"
].min()


# Finds the highest home value in the displayed period.
y_max = chart_df[
    "home_value"
].max()


# Creates lower padding for the Y-axis.
y_lower = y_min * 0.90


# Creates upper padding for the Y-axis.
y_upper = y_max * 1.10


# Creates the Altair home value line chart.
home_value_chart = (
    alt.Chart(
        chart_df
    )
    .mark_line(
        point=False
    )
    .encode(

        # Places date on the X-axis.
        x=alt.X(
            "date:T",
            title="Year",
            axis=alt.Axis(
                format="%Y"
            )
        ),

        # Places home value on the Y-axis.
        y=alt.Y(
            "home_value:Q",
            title="Typical Home Value",
            scale=alt.Scale(
                domain=[
                    y_lower,
                    y_upper
                ],
                zero=False
            ),
            axis=alt.Axis(
                format="$,.0f"
            )
        ),

        # Adds hover information.
        tooltip=[
            alt.Tooltip(
                "date:T",
                title="Date",
                format="%B %Y"
            ),
            alt.Tooltip(
                "home_value:Q",
                title="Home Value",
                format="$,.0f"
            )
        ]
    )
    .properties(
        height=450
    )
)


# Displays the home value trend chart.
st.altair_chart(
    home_value_chart,
    use_container_width=True
)


# Adds a divider between dashboard sections.
st.divider()


# Displays the national comparison section.
st.subheader(
    "Home Value Comparison by State"
)


# Finds the latest home value record for every state.
latest_home_by_state = (
    home_df.sort_values(
        "date"
    )
    .groupby(
        "state_name",
        as_index=False
    )
    .tail(1)
    .copy()
)


# Sorts states from highest to lowest home value.
latest_home_by_state = latest_home_by_state.sort_values(
    "home_value",
    ascending=False
).reset_index(
    drop=True
)


# Creates the national home value rank.
latest_home_by_state[
    "national_rank"
] = latest_home_by_state.index + 1


# Finds the selected state's national rank.
selected_state_rank = latest_home_by_state.loc[
    latest_home_by_state["state_name"] == selected_state,
    "national_rank"
].iloc[0]


# Finds the selected state's latest home value.
selected_state_home_value = latest_home_by_state.loc[
    latest_home_by_state["state_name"] == selected_state,
    "home_value"
].iloc[0]


# Creates two columns for comparison metrics.
comparison_col1, comparison_col2 = st.columns(2)


# Displays the selected state's national home value rank.
with comparison_col1:
    st.metric(
        label="National Home Value Rank",
        value=f"#{selected_state_rank}"
    )


# Displays the selected state's home value.
with comparison_col2:
    st.metric(
        label=f"{selected_state} Home Value",
        value=f"${selected_state_home_value:,.0f}"
    )


# Selects the 15 states with the highest home values.
top_states = latest_home_by_state.head(
    15
).copy()


# Checks whether the selected state is already in the top 15.
selected_state_in_top = (
    selected_state
    in top_states["state_name"].values
)


# Adds the selected state if it is outside the top 15.
if not selected_state_in_top:

    # Finds the selected state's record.
    selected_state_row = latest_home_by_state[
        latest_home_by_state["state_name"] == selected_state
    ].copy()

    # Combines the top 15 states with the selected state.
    comparison_df = pd.concat(
        [
            top_states,
            selected_state_row
        ],
        ignore_index=True
    )

else:

    # Uses the existing top 15 if the selected state is already included.
    comparison_df = top_states.copy()


# Creates labels containing the state and national rank.
comparison_df[
    "state_label"
] = (
    comparison_df["state_name"]
    + " (#"
    + comparison_df["national_rank"].astype(str)
    + ")"
)


# Creates the national comparison bar chart.
comparison_chart = (
    alt.Chart(
        comparison_df
    )
    .mark_bar()
    .encode(

        # Places home value on the X-axis.
        x=alt.X(
            "home_value:Q",
            title="Typical Home Value",
            axis=alt.Axis(
                format="$,.0f"
            )
        ),

        # Places states on the Y-axis.
        y=alt.Y(
            "state_label:N",
            title=None,
            sort=alt.SortField(
                field="home_value",
                order="descending"
            )
        ),

        # Makes the selected state stand out.
        opacity=alt.condition(
            alt.datum.state_name == selected_state,
            alt.value(1.0),
            alt.value(0.45)
        ),

        # Displays detailed information when hovering.
        tooltip=[
            alt.Tooltip(
                "state_name:N",
                title="State"
            ),
            alt.Tooltip(
                "national_rank:Q",
                title="National Rank"
            ),
            alt.Tooltip(
                "home_value:Q",
                title="Home Value",
                format="$,.0f"
            ),
            alt.Tooltip(
                "date:T",
                title="Latest Data",
                format="%B %Y"
            )
        ]
    )
    .properties(
        height=550
    )
)


# Displays the national comparison chart.
st.altair_chart(
    comparison_chart,
    use_container_width=True
)