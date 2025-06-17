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

# Create output directory if it doesn't exist
output_dir = "powerbi_integration/output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


def process_sp500_index_data(
    input_path="data/sp500_index.csv",
    output_path="powerbi_integration/output/sp500_index_processed.csv",
):
    """
    Process S&P 500 index data, calculate metrics, and export to CSV.
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
    Process S&P 500 companies data and export to CSV.
    """
    # Read the data
    df = pd.read_csv(input_path)

    # Ensure Date column is in datetime format
    df["Date"] = pd.to_datetime(df["Date"])

    # Additional processing can be added here if needed (e.g., sector analysis)

    # Save the processed data
    df.to_csv(output_path, index=False)
    print(f"Processed S&P 500 companies data saved to {output_path}")
    return df


def process_berkshire_portfolio_data(
    input_path="data/berkshire_porfolio.csv",
    output_path="powerbi_integration/output/berkshire_portfolio_processed.csv",
):
    """
    Process Berkshire Hathaway portfolio data and export to CSV.
    """
    # Read the data
    df = pd.read_csv(input_path)

    # Additional processing or enrichment can be added here if needed
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
