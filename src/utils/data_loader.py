# ─────────────────────────────────────────────────────────────────────────────
# data_loader.py — Transcript File Loader
#
# WHAT THIS FILE DOES:
#   Reads the input Excel file that contains call transcripts and loads it
#   into a pandas DataFrame so the pipeline can process it row by row.
#
# WHY pandas?
#   pandas is the standard Python library for working with table data.
#   A DataFrame is like a spreadsheet in memory — you can loop through rows,
#   add columns, merge tables, and save results very easily.
#
# WHY read_excel()?
#   The transcripts are stored in an Excel file (.xlsx). read_excel() loads
#   that file directly into a DataFrame without needing to convert it first.
#   Use read_csv() instead if your file is in CSV format.
#
# EXPECTED FILE FORMAT:
#   The Excel file should have at least these two columns:
#     - call_id    : A unique ID for each call (e.g., "CALL001")
#     - transcript : The full text of the customer support conversation
#
# BEST PRACTICE:
#   Keep the default file path as a parameter with a default value so the
#   function works out of the box, but can also accept a different path when needed.
#
# WHEN TO USE THIS:
#   Called at the start of main.py to load the batch of transcripts to process.
# ─────────────────────────────────────────────────────────────────────────────

import pandas as pd


def load_transcripts(file_path: str = "data/transcripts.xlsx") -> pd.DataFrame:
    """
    Loads call transcripts from an Excel file into a pandas DataFrame.

    Args:
        file_path: Path to the .xlsx file. Defaults to "data/transcripts.xlsx".

    Returns:
        A DataFrame with one row per call transcript.
    """
    df = pd.read_excel(file_path)
    return df