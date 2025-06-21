"""
powerbi_data_export_db_test.py

This script contains functional tests for the database integration in powerbi_data_export.py.
It validates the creation of the SQLite database, schema correctness, data storage, and querying capabilities.

Usage:
    Run this script to execute tests:
    ```bash
    python powerbi_integration/powerbi_data_export_db_test.py
    ```
"""

import unittest
import os
import pandas as pd
from sqlalchemy import create_engine, inspect
from powerbi_integration.powerbi_data_export import (
    engine,
    sp500_index_table,
    sp500_companies_table,
    berkshire_portfolio_table,
    Session,
    process_sp500_index_data,
    process_sp500_companies_data,
    process_berkshire_portfolio_data,
)


class TestDatabaseIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.db_path = "powerbi_integration/output/financial_data.db"
        self.test_data_dir = "powerbi_integration/test_data"
        os.makedirs(self.test_data_dir, exist_ok=True)

        # Create small test datasets
        self.create_test_data()

    def create_test_data(self):
        """Create small test datasets for validation."""
        # S&P 500 Index test data
        sp500_index_data = {
            "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "Close": [4000.0, 4050.0, 4100.0],
        }
        sp500_index_df = pd.DataFrame(sp500_index_data)
        sp500_index_df.to_csv(f"{self.test_data_dir}/sp500_index_test.csv", index=False)

        # S&P 500 Companies test data
        sp500_companies_data = {
            "Date": ["2023-01-01", "2023-01-01"],
            "Symbol": ["AAPL", "MSFT"],
            "Close": [175.0, 250.0],
            "Sector": ["Technology", "Technology"],
        }
        sp500_companies_df = pd.DataFrame(sp500_companies_data)
        sp500_companies_df.to_csv(
            f"{self.test_data_dir}/sp500_companies_test.csv", index=False
        )

        # Berkshire Portfolio test data
        berkshire_data = {
            "Company": ["Apple Inc.", "Bank of America"],
            "Ticker": ["AAPL", "BAC"],
            "Shares": [1000000, 500000],
            "Value": [175000000.0, 15000000.0],
            "Weight": [0.5, 0.1],
        }
        berkshire_df = pd.DataFrame(berkshire_data)
        berkshire_df.to_csv(
            f"{self.test_data_dir}/berkshire_portfolio_test.csv", index=False
        )

    def test_database_connection(self):
        """Test if the database connection is established and file exists."""
        self.assertTrue(os.path.exists(self.db_path), "Database file should exist")
        conn = engine.connect()
        self.assertIsNotNone(conn, "Database connection should be established")
        conn.close()

    def test_table_creation(self):
        """Test if tables are created with correct schema."""
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        self.assertIn("sp500_index", tables, "S&P 500 index table should exist")
        self.assertIn("sp500_companies", tables, "S&P 500 companies table should exist")
        self.assertIn(
            "berkshire_portfolio", tables, "Berkshire portfolio table should exist"
        )

        # Check columns for sp500_index
        columns = [col["name"] for col in inspector.get_columns("sp500_index")]
        expected_columns = ["id", "Date", "Close", "50ma", "200ma", "Return", "Year"]
        for col in expected_columns:
            self.assertIn(
                col, columns, f"Column {col} should exist in sp500_index table"
            )

    def test_sp500_index_storage_and_query(self):
        """Test storage and querying of S&P 500 index data."""
        input_path = f"{self.test_data_dir}/sp500_index_test.csv"
        output_path = f"{self.test_data_dir}/sp500_index_processed_test.csv"
        df = process_sp500_index_data(input_path, output_path)

        session = Session()
        try:
            count = session.execute("SELECT COUNT(*) FROM sp500_index").fetchone()[0]
            self.assertEqual(count, len(df), "All records should be stored in database")

            latest_year = df["Year"].max()
            query_result = session.execute(
                sp500_index_table.select().where(
                    sp500_index_table.c.Year == latest_year
                )
            ).fetchall()
            self.assertEqual(
                len(query_result),
                len(df[df["Year"] == latest_year]),
                "Query should return correct number of records for the latest year",
            )
        finally:
            session.close()

    def test_sp500_companies_storage_and_query(self):
        """Test storage and querying of S&P 500 companies data."""
        input_path = f"{self.test_data_dir}/sp500_companies_test.csv"
        output_path = f"{self.test_data_dir}/sp500_companies_processed_test.csv"
        df = process_sp500_companies_data(input_path, output_path)

        session = Session()
        try:
            count = session.execute("SELECT COUNT(*) FROM sp500_companies").fetchone()[
                0
            ]
            self.assertEqual(count, len(df), "All records should be stored in database")

            sectors = session.execute(
                "SELECT DISTINCT Sector FROM sp500_companies"
            ).fetchall()
            self.assertEqual(
                len(sectors),
                len(df["Sector"].unique()),
                "Query should return correct number of distinct sectors",
            )
        finally:
            session.close()

    def test_berkshire_portfolio_storage_and_query(self):
        """Test storage and querying of Berkshire Hathaway portfolio data."""
        input_path = f"{self.test_data_dir}/berkshire_portfolio_test.csv"
        output_path = f"{self.test_data_dir}/berkshire_portfolio_processed_test.csv"
        df = process_berkshire_portfolio_data(input_path, output_path)

        session = Session()
        try:
            count = session.execute(
                "SELECT COUNT(*) FROM berkshire_portfolio"
            ).fetchone()[0]
            self.assertEqual(count, len(df), "All records should be stored in database")

            top_holdings = session.execute(
                "SELECT Company, Value FROM berkshire_portfolio ORDER BY Value DESC LIMIT 1"
            ).fetchone()
            self.assertEqual(
                top_holdings[0],
                df.loc[df["Value"].idxmax(), "Company"],
                "Query should return the company with the highest value",
            )
        finally:
            session.close()


if __name__ == "__main__":
    unittest.main()
