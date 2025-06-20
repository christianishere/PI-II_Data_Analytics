# Usage Instructions for Financial Data Processing Project

This document provides detailed instructions on how to execute the scripts and tests related to the "Analisis de Datos 1" class project focused on financial data processing for Power BI integration with SQLAlchemy database functionality.

## Running the Data Processing Script

To execute the script for processing financial data with database integration, use the following command from the root of the project directory:

```bash
python powerbi_integration/powerbi_data_export.py
```

This command will:

- Process input data from CSV files located in the `data/` directory.
- Store the processed data in a SQLite database at `powerbi_integration/output/financial_data.db`.
- Export the results to CSV files in `powerbi_integration/output/` for importation into Power BI.

## Running the Functional Tests

To execute the functional tests that validate the database integration, use the following command from the root of the project directory:

```bash
python powerbi_integration/powerbi_data_export_db_test.py
```

This command will:

- Run a series of unit tests to verify database connection, table creation, data storage, and querying capabilities.
- Generate temporary test data in `powerbi_integration/test_data/` to validate the functionalities.

These instructions ensure that users can replicate the data processing workflow and verify the integrity of the database integration for the project.
