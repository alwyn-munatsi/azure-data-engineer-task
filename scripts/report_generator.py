"""
Simple PDF report generator for the StabilityApp.

This module queries the local StabilityApp database for the most recent
submission that contains an email address, then renders a small PDF
containing user information and indicator scores. The intent is to
produce a shareable 'stability evaluation' report for demonstration or
emailing to a user.

Assumptions:
- The database schema contains Submissions, SubmissionScores, Indicators,
  AgeRanges and Regions tables.
- At least one submission with a non-null email exists when the script
  runs; otherwise the script prints a message and exits.
"""

import pandas as pd
import pyodbc
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

# Connection string used by pyodbc. Update SERVER/DATABASE to match your
# environment if different. TrustServerCertificate is enabled for local
# development convenience.
connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=ALWYN-PC\\SQLEXPRESS;"
    "DATABASE=StabilityApp;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


def generate_sample_report():
    """Generate a PDF report for the most recent submission that has an email.

    The function performs three main steps:
    1. Query the database for a submission ID that has an email.
    2. Load submission details and associated indicator scores.
    3. Render a simple PDF containing the user's details and scores.
    """

    print("Generating sample PDF report...")

    # Open a DB connection and cursor. We close the connection after reading
    # the required rows to avoid holding DB resources while creating the PDF.
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    # Find the latest submission that includes an email so we can generate a
    # report for a contactable user. TOP 1 ensures we only fetch one row.
    cursor.execute("""
        SELECT TOP 1 submission_id FROM Submissions 
        WHERE email IS NOT NULL 
        ORDER BY created_at DESC
    """)

    result = cursor.fetchone()
    if not result:
        # No available submission with an email — nothing to generate.
        print("No submissions with email found!")
        return

    submission_id = result[0]

    # Retrieve submission details and join lookup tables for readable labels
    # (age range and region). We use LEFT JOIN so missing lookups don't fail
    # the query — the code will display 'N/A' for missing values later.
    cursor.execute("""
        SELECT s.submission_id, s.created_at, s.instability_ratio,
               s.first_name, s.last_name, s.email,
               ar.age_range_label, r.region_name
        FROM Submissions s
        LEFT JOIN AgeRanges ar ON s.age_range_id = ar.age_range_id
        LEFT JOIN Regions r ON s.region_id = r.region_id
        WHERE s.submission_id = ?
    """, submission_id)

    submission = cursor.fetchone()

    # Fetch all indicator scores for this submission and convert to a dict
    # mapping indicator name -> numeric score for convenient rendering.
    cursor.execute("""
        SELECT i.indicator_name, ss.score_value
        FROM SubmissionScores ss
        JOIN Indicators i ON ss.indicator_id = i.indicator_id
        WHERE ss.submission_id = ?
    """, submission_id)

    scores = {row.indicator_name: row.score_value for row in cursor.fetchall()}

    # We can close the DB connection now — PDF generation is purely local.
    conn.close()

    # Build filename using the submission ID so it's easy to correlate files
    # with database records. Keep PDF generation simple using ReportLab's
    # high-level Platypus API (Paragraph, Table, Spacer, etc.).
    filename = f"stability_report_{submission_id}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []  # the document flowable list
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("STABILITY EVALUATION REPORT", styles['Heading1'])
    story.append(title)
    story.append(Spacer(1, 20))

    # User Information table: defensive access using `or` to display 'N/A'
    # when fields are None/empty. created_at is formatted as YYYY-MM-DD.
    user_data = [
        ["Name:", f"{submission.first_name or 'N/A'} {submission.last_name or ''}"],
        ["Email:", submission.email or 'N/A'],
        ["Submission Date:", submission.created_at.strftime('%Y-%m-%d')],
        ["Region:", submission.region_name or 'N/A'],
        ["Age Range:", submission.age_range_label or 'N/A']
    ]

    # Table layout for user info with simple styling. Column widths chosen to
    # give the label a narrow column and the value a wider column.
    user_table = Table(user_data, colWidths=[100, 400])
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    story.append(user_table)
    story.append(Spacer(1, 20))

    # Scores section header
    story.append(Paragraph("Indicator Scores", styles['Heading2']))

    # Prepare data for the scores table; include a header row first.
    score_data = [['Indicator', 'Score']]
    for indicator, score in scores.items():
        # Convert the score to a string for table rendering. If there are no
        # scores this loop simply won't add rows.
        score_data.append([indicator, str(score)])

    # Append the overall instability ratio as an additional row. Use
    # formatting to show two decimal places.
    score_data.append(['Instability Ratio', f"{submission.instability_ratio:.2f}"])

    # Create the table for scores with a darker header and a subtle body
    # background color to improve readability.
    score_table = Table(score_data, colWidths=[350, 150])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(score_table)

    # Build the PDF file from the assembled flowables. This is a synchronous
    # operation that writes `filename` to disk in the current working directory.
    doc.build(story)
    print(f"PDF report generated: {filename}")


if __name__ == "__main__":
    generate_sample_report()