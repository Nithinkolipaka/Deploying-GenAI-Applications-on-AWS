# ─────────────────────────────────────────────────────────────────────────────
# helpers.py — General Utility Functions
#
# WHAT THIS FILE DOES:
#   Contains small helper functions used across the project.
#   Currently has one function: saving a DataFrame to an Excel file.
#
# WHY to_excel() AND NOT to_csv()?
#   Excel files are easier for non-technical users to open and read.
#   They support multiple sheets, formatting, and are the standard
#   format in most business and QA workflows.
#   Use index=False to avoid saving the row numbers as an extra column.
#
# WHY A HELPERS FILE?
#   Keeps small, reusable utility functions in one place so you don't
#   repeat the same code in multiple files. If you need to change how
#   files are saved (e.g., add formatting), you only change it here.
#
# BEST PRACTICE:
#   Use a default file path so the function works with no arguments,
#   but can still accept a custom path when needed.
#
# WHEN TO USE THIS:
#   Called at the end of main.py to save the final evaluated DataFrame.
# ─────────────────────────────────────────────────────────────────────────────

import pandas as pd


def save_dataframe(df: pd.DataFrame, file_path: str = "data/output.xlsx"):
    """
    Saves a DataFrame to an Excel file.

    Args:
        df:        The DataFrame to save.
        file_path: Where to save the file. Defaults to "data/output.xlsx".

    Note:
        index=False prevents pandas from adding an extra row-number column.
    """
    df.to_excel(file_path, index=False)