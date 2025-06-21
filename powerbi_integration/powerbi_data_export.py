"""
powerbi_data_export.py

This script processes financial data for the "Mercado Bursátil y S&P 500 App" and exports it in a format suitable for Power BI import.
It reads existing CSV files, performs necessary calculations (e.g., moving averages, returns), and saves the processed data into structured CSV files.
The goal is to facilitate the transition of visualizations from Streamlit to Power BI.

Usage:
    Run this script to process and export data:
    ```bash
    python powerbi_integration/powerbi_data_export.py
    ```
    After execution, import the generated CSV files into Power BI Desktop for visualization.

Input Files:
    - data/sp500_index.csv: Historical data for the S&P 500 index.
    - data/sp500_data.csv: Data for individual S&P 500 companies.
    - data/berkshire_porfolio.csv: Berkshire Hathaway portfolio data.

Output Files:
    - powerbi_integration/output/sp500_index_processed.csv: Processed S&P 500 index data with calculated metrics.
    - powerbi_integration/output/sp500_companies_processed.csv: Processed data for S&P 500 companies.
    - powerbi_integration/output/berkshire_portfolio_processed.csv: Processed Berkshire Hathaway portfolio data.
"""

import pandas as pd
import os
import yfinance as yf
from datetime import datetime
import numpy as np
from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    MetaData,
)
from sqlalchemy.orm import sessionmaker
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)

# Create output directory if it doesn't exist
output_dir = "powerbi_integration/output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Database setup
DB_PATH = "powerbi_integration/output/financial_data.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
metadata = MetaData()

# Define tables
sp500_index_table = Table(
    "sp500_index",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("Date", DateTime),
    Column("Close", Float),
    Column("50ma", Float),
    Column("200ma", Float),
    Column("Return", Float),
    Column("Year", Integer),
)

sp500_companies_table = Table(
    "sp500_companies",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("Date", DateTime),
    Column("Symbol", String),
    Column("Close", Float),
    Column("Sector", String),
)

berkshire_portfolio_table = Table(
    "berkshire_portfolio",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("Company", String),
    Column("Ticker", String),
    Column("Shares", Float),
    Column("Value", Float),
    Column("Weight", Float),
)

# Create tables if they don't exist
metadata.create_all(engine)

# Set up session for database operations
Session = sessionmaker(bind=engine)


def process_sp500_index_data(
    input_path="data/sp500_index.csv",
    output_path="powerbi_integration/output/sp500_index_processed.csv",
):
    """
    Process S&P 500 index data, calculate metrics, store in database, and export to CSV.
    """
    # Read the data
    df = pd.read_csv(input_path)

    # Ensure Date column is in datetime format
    df["Date"] = pd.to_datetime(df["Date"])

    # Calculate moving averages if not already present
    if "50ma" not in df.columns:
        df["50ma"] = df["Close"].rolling(window=50).mean()
    if "200ma" not in df.columns:
        df["200ma"] = df["Close"].rolling(window=200).mean()

    # Calculate daily return if not already present
    if "Return" not in df.columns:
        df["Return"] = df["Close"].pct_change()

    # Calculate annualized return by year
    df["Year"] = df["Date"].dt.year
    yearly_return = df.groupby("Year")["Close"].last().pct_change() * 100
    yearly_return_df = yearly_return.reset_index()
    yearly_return_df.columns = ["Year", "Annualized_Return_Percent"]
    yearly_return_df["Up_Down"] = yearly_return_df["Annualized_Return_Percent"] > 0
    yearly_return_df["Up_Down"] = yearly_return_df["Up_Down"].replace(
        {True: "Up", False: "Down"}
    )

    # Store data in database
    session = Session()
    try:
        # Clear existing data to avoid duplicates
        session.execute(sp500_index_table.delete())
        session.commit()
        log.info("Cleared existing S&P 500 index data from database.")

        # Insert new data
        data_to_insert = df.to_dict("records")
        session.execute(sp500_index_table.insert(), data_to_insert)
        session.commit()
        log.info(
            f"Stored {len(data_to_insert)} records of S&P 500 index data in database."
        )
    except Exception as e:
        log.error(f"Error storing S&P 500 index data in database: {e}")
        session.rollback()
    finally:
        session.close()

    # Query example: Get data for the last year
    latest_year = df["Year"].max()
    session = Session()
    try:
        query_result = session.execute(
            sp500_index_table.select().where(sp500_index_table.c.Year == latest_year)
        ).fetchall()
        log.info(
            f"Queried {len(query_result)} records for year {latest_year} from database."
        )
    except Exception as e:
        log.error(f"Error querying S&P 500 index data: {e}")
    finally:
        session.close()

    # Save the processed data
    df.to_csv(output_path, index=False)
    yearly_return_df.to_csv(
        output_path.replace(".csv", "_annual_returns.csv"), index=False
    )

    print(f"Processed S&P 500 index data saved to {output_path}")
    print(
        f"Annual returns data saved to {output_path.replace('.csv', '_annual_returns.csv')}"
    )
    return df


def process_sp500_companies_data(
    input_path="data/sp500_data.csv",
    output_path="powerbi_integration/output/sp500_companies_processed.csv",
):
    """
    Process S&P 500 companies data, store in database, and export to CSV.
    """
    # Read the data
    df = pd.read_csv(input_path)
    # Validate input data
    if not validate_input_data(df, "S&P 500 Companies"):
        log(
            "Proceeding despite validation issues. Results may be incomplete or inaccurate."
        )

    # Ensure Date column is in datetime format
    df["Date"] = pd.to_datetime(df["Date"])

    # Additional processing can be added here if needed (e.g., sector analysis)

    # Store data in database
    session = Session()
    try:
        # Clear existing data to avoid duplicates
        session.execute(sp500_companies_table.delete())
        session.commit()
        log.info("Cleared existing S&P 500 companies data from database.")

        # Insert new data
        data_to_insert = df.to_dict("records")
        session.execute(sp500_companies_table.insert(), data_to_insert)
        session.commit()
        log.info(
            f"Stored {len(data_to_insert)} records of S&P 500 companies data in database."
        )
    except Exception as e:
        log.error(f"Error storing S&P 500 companies data in database: {e}")
        session.rollback()
    finally:
        session.close()

    # Query example: Get distinct sectors
    session = Session()
    try:
        sectors = session.execute(
            "SELECT DISTINCT Sector FROM sp500_companies"
        ).fetchall()
        log.info(
            f"Queried {len(sectors)} distinct sectors from S&P 500 companies data."
        )
    except Exception as e:
        log.error(f"Error querying S&P 500 companies data: {e}")
    finally:
        session.close()

    # Save the processed data
    df.to_csv(output_path, index=False)
    print(f"Processed S&P 500 companies data saved to {output_path}")
    return df


def process_berkshire_portfolio_data(
    input_path="data/berkshire_porfolio.csv",
    output_path="powerbi_integration/output/berkshire_portfolio_processed.csv",
):
    """
    Process Berkshire Hathaway portfolio data, store in database, and export to CSV.
    """
    # Read the data
    df = pd.read_csv(input_path)
    # Validate input data
    if not validate_input_data(df, "Berkshire Hathaway Portfolio"):
        log(
            "Proceeding despite validation issues. Results may be incomplete or inaccurate."
        )

    # Additional processing or enrichment can be added here if needed

    # Store data in database
    session = Session()
    try:
        # Clear existing data to avoid duplicates
        session.execute(berkshire_portfolio_table.delete())
        session.commit()
        log.info("Cleared existing Berkshire Hathaway portfolio data from database.")

        # Insert new data
        data_to_insert = df.to_dict("records")
        session.execute(berkshire_portfolio_table.insert(), data_to_insert)
        session.commit()
        log.info(
            f"Stored {len(data_to_insert)} records of Berkshire Hathaway portfolio data in database."
        )
    except Exception as e:
        log.error(f"Error storing Berkshire Hathaway portfolio data in database: {e}")
        session.rollback()
    finally:
        session.close()

    # Query example: Get top holdings by value
    session = Session()
    try:
        top_holdings = session.execute(
            "SELECT Company, Value FROM berkshire_portfolio ORDER BY Value DESC LIMIT 5"
        ).fetchall()
        log.info(
            f"Queried top 5 holdings by value from Berkshire Hathaway portfolio data."
        )
    except Exception as e:
        log.error(f"Error querying Berkshire Hathaway portfolio data: {e}")
    finally:
        session.close()

    # For now, just export the data as is for Power BI
    df.to_csv(output_path, index=False)
    print(f"Processed Berkshire Hathaway portfolio data saved to {output_path}")
    return df


def main():
    """
    Main function to execute data processing and export for Power BI.
    """
    print("Starting data processing for Power BI integration...")

    # Process each dataset
    process_sp500_index_data()
    process_sp500_companies_data()
    process_berkshire_portfolio_data()

    print("Data processing complete. Files are ready for import into Power BI.")
    print("Steps to import into Power BI:")
    print("1. Open Power BI Desktop.")
    print(
        "2. Select 'Get Data' > 'Text/CSV' and navigate to the 'powerbi_integration/output/' directory."
    )
    print("3. Import each CSV file to recreate visualizations from the Streamlit app.")
    print("4. Use Power BI's features to build interactive dashboards and reports.")


if __name__ == "__main__":
    main()
