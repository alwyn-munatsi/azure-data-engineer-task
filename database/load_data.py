"""
Small utility to load survey response rows into the StabilityApp database.

This script reads a CSV file exported from the survey frontend, maps
string-valued lookups (age ranges, regions, indicators) to their
database surrogate keys, inserts submissions and related score rows,
and creates a report request for records that include an email.

The script is intentionally simple and synchronous. It assumes the
database already has the lookup rows populated (AgeRanges, Regions,
Indicators). Duplicated submission IDs are skipped.
"""

import pandas as pd
import pyodbc
import uuid
from datetime import datetime

print("=== Stability App Data Loader ===")

# Database connection string used by pyodbc. Adjust SERVER/DATABASE as needed.
connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=StabilityApp;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


def load_survey_data():
    """Read CSV rows and insert them into the database.

    Behavior and contract:
    - Input: CSV file at data/survey_responses_rows.csv; each row must have a
      UUID in the `id` column and an ISO timestamp in `created_at`.
    - Output: Inserts into Submissions, SubmissionScores and ReportRequests.
    - Errors: Invalid UUIDs are skipped; duplicate submission IDs are skipped
      (handled by catching IntegrityError). Any other exception triggers a
      rollback of the transaction.
    """

    print("1. Reading CSV file...")

    # Read CSV into a pandas DataFrame. We intentionally don't specify dtypes
    # here to allow for slight variations in input. Downstream code checks for
    # NaNs using pandas utilities before casting/using values.
    df = pd.read_csv('data/survey_responses_rows.csv')
    print(f"   Found {len(df)} records in CSV")

    print("2. Connecting to database...")
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    try:
        print("3. Loading lookup tables...")

        # Load lookup tables into Python dictionaries for fast mapping from the
        # CSV's string labels to the integer surrogate keys used by the DB.
        cursor.execute("SELECT age_range_id, age_range_label FROM AgeRanges")
        age_ranges = {row.age_range_label: row.age_range_id for row in cursor.fetchall()}
        print(f"   Age ranges: {age_ranges}")

        cursor.execute("SELECT region_id, region_name FROM Regions")
        regions = {row.region_name: row.region_id for row in cursor.fetchall()}
        print(f"   Regions: {regions}")

        cursor.execute("SELECT indicator_id, indicator_name FROM Indicators")
        indicators = {row.indicator_name: row.indicator_id for row in cursor.fetchall()}
        print(f"   Indicators: {indicators}")

        submissions_loaded = 0
        scores_loaded = 0

        print("4. Processing submissions...")

        # Iterate over CSV rows and insert into the DB. We use iterrows() which is
        # fine for relatively small datasets; for large volumes consider chunking
        # or using a bulk-load mechanism.
        for index, row in df.iterrows():
            if index % 50 == 0:  # simple progress indicator
                print(f"   Processed {index} records...")

            # Validate and parse the submission UUID. Skip rows with invalid IDs.
            try:
                submission_id = uuid.UUID(row['id'])
            except Exception:
                # Skip malformed or missing UUIDs instead of failing the whole run
                continue

            # Parse the ISO timestamp. The CSV may include a trailing +00:00
            # timezone; strip it before parsing to produce a naive datetime.
            created_at = datetime.fromisoformat(row['created_at'].replace('+00:00', ''))

            # Map CSV string labels to integer lookup IDs; allow None when the
            # CSV value is missing/NaN.
            age_range_id = age_ranges.get(row['age_range']) if pd.notna(row['age_range']) else None
            region_id = regions.get(row['region']) if pd.notna(row['region']) else None

            # Insert submission row. We catch IntegrityError to skip duplicate
            # primary keys (submission_id). Other exceptions will be rolled back
            # by the outer exception handler.
            try:
                cursor.execute("""
                    INSERT INTO Submissions (submission_id, created_at, age_range_id, region_id, 
                                           instability_ratio, first_name, last_name, email)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, submission_id, created_at, age_range_id, region_id,
                   row['instability_ratio'] if pd.notna(row['instability_ratio']) else None,
                   row['first_name'] if pd.notna(row['first_name']) else None,
                   row['last_name'] if pd.notna(row['last_name']) else None,
                   row['email'] if pd.notna(row['email']) else None)

                submissions_loaded += 1
            except pyodbc.IntegrityError:
                # Duplicate submission ID or constraint violation; skip this row
                continue

            # CSV -> indicator name mapping. The CSV uses rate columns named for
            # specific indicators; map those column names to the indicator label
            # stored in the Indicators lookup table.
            indicator_mapping = {
                'economic_management_rate': 'Economic Management',
                'immigration_policy_rate': 'Immigration Policy', 
                'foreign_policy_rate': 'Foreign Policy',
                'domestic_policy_rate': 'Domestic Policy', 
                'social_policy_rate': 'Social Policy'
            }

            # Insert scores for each non-empty score column. We cast to int
            # because CSV reading may produce floats by default (e.g. '3.0').
            for csv_col, indicator_name in indicator_mapping.items():
                if pd.notna(row[csv_col]):
                    cursor.execute("""
                        INSERT INTO SubmissionScores (submission_id, indicator_id, score_value)
                        VALUES (?, ?, ?)
                    """, submission_id, indicators[indicator_name], int(row[csv_col]))
                    scores_loaded += 1

            # If an email was provided, create a ReportRequests row with status
            # 'completed' so downstream processes know a report has been generated.
            if pd.notna(row['email']) and row['email'].strip():
                cursor.execute("""
                    INSERT INTO ReportRequests (submission_id, status)
                    VALUES (?, 'completed')
                """, submission_id)

        # Commit the transaction when all rows are processed.
        conn.commit()
        print("5. Data loading completed!")
        print(f"   Submissions loaded: {submissions_loaded}")
        print(f"   Scores loaded: {scores_loaded}")

    except Exception as e:
        # Roll back any partial changes on unexpected errors.
        conn.rollback()
        print(f"ERROR: {e}")
    finally:
        # Always ensure we close the connection.
        conn.close()


if __name__ == "__main__":
    load_survey_data()