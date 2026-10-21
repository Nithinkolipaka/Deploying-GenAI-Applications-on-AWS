# ─────────────────────────────────────────────────────────────────────────────
# template.py — Project Folder & File Setup Script
#
# WHAT THIS FILE DOES:
#   Run this script ONCE at the very beginning to create all the folders and
#   empty files needed for this project. It sets up the correct project structure
#   so you don't have to create each folder manually.
#
# WHEN TO USE THIS:
#   Only run this once when starting the project from scratch.
#   Run it with: python template.py
#
# BEST PRACTICE:
#   Keeping a setup script like this makes it easy for any new developer
#   to get the project structure ready in one command.
# ─────────────────────────────────────────────────────────────────────────────

import os

# List of folders to create
folders = [
    "src",
    "src/components",
    "src/pipeline",
    "src/utils",
    "config",
    "data",
    "logs"
]

# List of files to create with their starting content (empty by default)
files = {
    # Package marker files — tells Python these folders are importable modules
    "src/__init__.py": "",
    "src/components/__init__.py": "",
    "src/pipeline/__init__.py": "",
    "src/utils/__init__.py": "",

    # Core logic components
    "src/components/classification.py": "",
    "src/components/evaluation.py": "",
    "src/components/router.py": "",
    "src/components/aggregation.py": "",
    "src/components/reporting.py": "",

    # Pipeline orchestration
    "src/pipeline/pipeline.py": "",

    # Utility helpers
    "src/utils/config_loader.py": "",
    "src/utils/llm_loader.py": "",
    "src/utils/data_loader.py": "",
    "src/utils/helpers.py": "",

    # Log file placeholder
    "logs/app.log": ""
}

# Create all folders (exist_ok=True means no error if they already exist)
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Create all files only if they do not already exist (to avoid overwriting work)
for file_path, content in files.items():
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write(content)

print("✅ Project structure created successfully!")