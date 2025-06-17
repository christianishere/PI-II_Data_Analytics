"""
powerbi_data_export_test.py

This script is a debugging version of 'powerbi_data_export.py'. It processes financial data for the "Mercado Bursátil y S&P 500 App"
and exports it in a format suitable for Power BI import. Unlike the original script, this version includes interactive prompts
and detailed logging to help step through the process, inspect data at each stage, and identify any issues.

Usage:
    Run this script in the terminal to process data step-by-step:
    ```bash
    python powerbi_integration/powerbi_data_export_test.py
    ```
    Follow the prompts to proceed through each step or inspect the data. Intermediate results and logs will be displayed in the terminal.

Input Files:
    - data/sp500_index.csv: Historical data for the S&P 500 index.
    - data/sp500_data.csv: Data for individual S&P 500 companies.
    - data/berkshire_porfolio.csv: Berkshire Hathaway portfolio data.

Output Files:
    - powerbi_integration/debug_output/sp500_index_processed.csv: Processed S&P 500 index data with calculated metrics.
    - powerbi_integration/debug_output/sp500_companies_processed.csv: Processed data for S&P 500 companies.
    - powerbi_integration/debug_output/berkshire_portfolio_processed.csv: Processed Berkshire Hathaway portfolio data.
    - powerbi_integration/debug_output/debug_log.txt: Log file with detailed information about each step and any errors.
"""

import pandas as pd
import os
import yfinance as yf
from datetime import datetime
import numpy as np

# Create debug output directory if it doesn't exist
debug_dir = "powerbi_integration/debug_output"
if not os.path.exists(debug_dir):
    os.makedirs(debug_dir)

# Initialize a log file
log_file = os.path.join(debug_dir, "debug_log.txt")


def log(message):
    """Write a message to the log file and print to terminal."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}\n"
    print(log_message.strip())
    with open(log_file, "a") as f:
        f.write(log_message)


# Function to prompt user for continuation
def prompt_user(message):
    """Prompt user to continue or inspect data."""
    response = input(f"{message} (y/n): ").strip().lower()
    return response == "y"


def display_dataframe(df, name, rows=5):
    """Display basic information about a DataFrame."""
    log(f"--- {name} DataFrame Info ---")
    log(f"Shape: {df.shape}")
    log(f"Columns: {list(df.columns)}")
    log(f"First {rows} rows:\n{df.head(rows).to_string()}")
    log(f"--- End of {name} Info ---")


def process_sp500_index_data(
    input_path="data/sp500_index.csv",
    output_path="powerbi_integration/debug_output/sp500_index_processed.csv",
):
    """
    Process S&P 500 index data, calculate metrics, and export to CSV with debugging steps.
    """
    log("Starting processing of S&P 500 index data...")

    # Step 1: Read the data
    try:
        df = pd.read_csv(input_path)
        log(f"Successfully read {input_path}")
        display_dataframe(df, "S&P 500 Index Raw")
    except Exception as e:
        log(f"Error reading {input_path}: {str(e)}")
        log("Check if the file exists and is accessible. Path: " + input_path)
        return None

    if not prompt_user("Data read complete. Continue to Date conversion?"):
        log("User chose to stop at data reading step.")
        return None

    # Step 2: Ensure Date column is in datetime format
    try:
        df["Date"] = pd.to_datetime(df["Date"])
        log("Date column converted to datetime format.")
        display_dataframe(df, "S&P 500 Index with Date Converted")
    except Exception as e:
        log(f"Error converting Date column: {str(e)}")
        log("Check if the 'Date' column exists and contains valid date strings.")
        return None

    if not prompt_user(
        "Date conversion complete. Continue to calculate moving averages?"
    ):
        log("User chose to stop at Date conversion step.")
        return None

    # Step 3: Calculate moving averages if not already present
    try:
        if "50ma" not in df.columns:
            df["50ma"] = df["Close"].rolling(window=50).mean()
            log("Calculated 50-day moving average.")
        else:
            log("50-day moving average already present in data.")
        if "200ma" not in df.columns:
            df["200ma"] = df["Close"].rolling(window=200).mean()
            log("Calculated 200-day moving average.")
        else:
            log("200-day moving average already present in data.")
        display_dataframe(df, "S&P 500 Index with Moving Averages")
    except Exception as e:
        log(f"Error calculating moving averages: {str(e)}")
        log("Check if 'Close' column exists and contains numeric data.")
        return None

    if not prompt_user(
        "Moving averages calculated. Continue to calculate daily returns?"
    ):
        log("User chose to stop at moving averages step.")
        return None

    # Step 4: Calculate daily return if not already present
    try:
        if "Return" not in df.columns:
            df["Return"] = df["Close"].pct_change()
            log("Calculated daily returns.")
        else:
            log("Daily returns already present in data.")
        display_dataframe(df, "S&P 500 Index with Daily Returns")
    except Exception as e:
        log(f"Error calculating daily returns: {str(e)}")
        log("Check if 'Close' column exists and contains numeric data.")
        return None

    if not prompt_user(
        "Daily returns calculated. Continue to calculate annualized returns?"
    ):
        log("User chose to stop at daily returns step.")
        return None

    # Step 5: Calculate annualized return by year
    try:
        # Ensure Date is in datetime format before extracting year
        if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            log("Re-converted Date column to datetime format for annualized returns.")
        df["Year"] = df["Date"].dt.year
        yearly_return = df.groupby("Year")["Close"].last().pct_change() * 100
        yearly_return_df = yearly_return.reset_index()
        yearly_return_df.columns = ["Year", "Annualized_Return_Percent"]
        yearly_return_df["Up_Down"] = yearly_return_df["Annualized_Return_Percent"] > 0
        yearly_return_df["Up_Down"] = yearly_return_df["Up_Down"].replace(
            {True: "Up", False: "Down"}
        )
        log("Calculated annualized returns by year.")
        display_dataframe(yearly_return_df, "S&P 500 Annualized Returns")
    except Exception as e:
        log(f"Error calculating annualized returns: {str(e)}")
        log("Check if 'Date' and 'Close' columns are correctly formatted.")
        return None

    if not prompt_user("Annualized returns calculated. Continue to save the data?"):
        log("User chose to stop at annualized returns step.")
        return None

    # Step 6: Save the processed data
    try:
        df.to_csv(output_path, index=False)
        yearly_return_df.to_csv(
            output_path.replace(".csv", "_annual_returns.csv"), index=False
        )
        log(f"Processed S&P 500 index data saved to {output_path}")
        log(
            f"Annual returns data saved to {output_path.replace('.csv', '_annual_returns.csv')}"
        )
    except Exception as e:
        log(f"Error saving processed data: {str(e)}")
        log("Check if you have write permissions in the output directory.")
        return None

    log("Completed processing of S&P 500 index data.")
    return df


def process_sp500_companies_data(
    input_path="data/sp500_data.csv",
    output_path="powerbi_integration/debug_output/sp500_companies_processed.csv",
):
    """
    Process S&P 500 companies data and export to CSV with debugging steps.
    """
    log("Starting processing of S&P 500 companies data...")

    # Step 1: Read the data
    try:
        df = pd.read_csv(input_path)
        log(f"Successfully read {input_path}")
        display_dataframe(df, "S&P 500 Companies Raw")
    except Exception as e:
        log(f"Error reading {input_path}: {str(e)}")
        log("Check if the file exists and is accessible. Path: " + input_path)
        return None

    if not prompt_user("Data read complete. Continue to Date conversion?"):
        log("User chose to stop at data reading step.")
        return None

    # Step 2: Ensure Date column is in datetime format
    try:
        df["Date"] = pd.to_datetime(df["Date"])
        log("Date column converted to datetime format.")
        display_dataframe(df, "S&P 500 Companies with Date Converted")
    except Exception as e:
        log(f"Error converting Date column: {str(e)}")
        log("Check if the 'Date' column exists and contains valid date strings.")
        return None

    if not prompt_user("Date conversion complete. Continue to save the data?"):
        log("User chose to stop at Date conversion step.")
        return None

    # Step 3: Save the processed data
    try:
        df.to_csv(output_path, index=False)
        log(f"Processed S&P 500 companies data saved to {output_path}")
    except Exception as e:
        log(f"Error saving processed data: {str(e)}")
        log("Check if you have write permissions in the output directory.")
        return None

    log("Completed processing of S&P 500 companies data.")
    return df


def process_berkshire_portfolio_data(
    input_path="data/berkshire_porfolio.csv",
    output_path="powerbi_integration/debug_output/berkshire_portfolio_processed.csv",
):
    """
    Process Berkshire Hathaway portfolio data and export to CSV with debugging steps.
    """
    log("Starting processing of Berkshire Hathaway portfolio data...")

    # Step 1: Read the data
    try:
        df = pd.read_csv(input_path)
        log(f"Successfully read {input_path}")
        display_dataframe(df, "Berkshire Hathaway Portfolio Raw")
    except Exception as e:
        log(f"Error reading {input_path}: {str(e)}")
        log("Check if the file exists and is accessible. Path: " + input_path)
        return None

    if not prompt_user("Data read complete. Continue to save the data?"):
        log("User chose to stop at data reading step.")
        return None

    # Step 2: Save the processed data
    try:
        df.to_csv(output_path, index=False)
        log(f"Processed Berkshire Hathaway portfolio data saved to {output_path}")
    except Exception as e:
        log(f"Error saving processed data: {str(e)}")
        log("Check if you have write permissions in the output directory.")
        return None

    log("Completed processing of Berkshire Hathaway portfolio data.")
    return df


def main():
    """
    Main function to execute data processing and export for Power BI with debugging steps.
    """
    log("Starting data processing for Power BI integration in debug mode...")
    log(
        "This script will pause at each step to allow inspection. Follow the prompts in the terminal."
    )

    if not prompt_user("Ready to process S&P 500 index data?"):
        log("User chose to skip S&P 500 index data processing.")
    else:
        process_sp500_index_data()

    if not prompt_user("Ready to process S&P 500 companies data?"):
        log("User chose to skip S&P 500 companies data processing.")
    else:
        process_sp500_companies_data()

    if not prompt_user("Ready to process Berkshire Hathaway portfolio data?"):
        log("User chose to skip Berkshire Hathaway portfolio data processing.")
    else:
        process_berkshire_portfolio_data()

    log(
        "Data processing complete in debug mode. Files are ready for import into Power BI or further inspection."
    )
    print("Steps to import into Power BI (once you have it installed):")
    print("1. Open Power BI Desktop.")
    print(
        "2. Select 'Get Data' > 'Text/CSV' and navigate to the 'powerbi_integration/debug_output/' directory."
    )
    print("3. Import each CSV file to recreate visualizations from the Streamlit app.")
    print("4. Use Power BI's features to build interactive dashboards and reports.")
    print(f"Debug log saved to {log_file} for review.")


if __name__ == "__main__":
    main()
