import os
import shutil
import subprocess
import sys

BASE_DIR = "BiteBuilderApp"
DB_FILE = os.path.join(BASE_DIR, "db.sqlite3")
MIGRATIONS = [
    os.path.join(BASE_DIR, "apps", "core", "migrations"),
    os.path.join(BASE_DIR, "apps", "users", "migrations"),
]

# Path to the current Python interpreter (inside venv)
PYTHON_EXEC = sys.executable

# Delete DB
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"🗑 Deleted {DB_FILE}")

# Delete migration files except __init__.py
for path in MIGRATIONS:
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        if item == "__init__.py":
            continue
        if os.path.isfile(full_path):
            os.remove(full_path)
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)
    print(f"🗑 Cleared {path}")

# Run migrations using the current Python (venv)
print("🔧 Rebuilding database...")
commands = [
    [PYTHON_EXEC, os.path.join(BASE_DIR, "manage.py"), "makemigrations", "users"],
    [PYTHON_EXEC, os.path.join(BASE_DIR, "manage.py"), "makemigrations", "core"],
    [PYTHON_EXEC, os.path.join(BASE_DIR, "manage.py"), "makemigrations"],
    [PYTHON_EXEC, os.path.join(BASE_DIR, "manage.py"), "migrate", "users"],
    [PYTHON_EXEC, os.path.join(BASE_DIR, "manage.py"), "migrate", "core"],
    [PYTHON_EXEC, os.path.join(BASE_DIR, "manage.py"), "migrate"],
    [PYTHON_EXEC, os.path.join(BASE_DIR, "manage.py"), "seed_nutrients"],
]
for cmd in commands:
    subprocess.run(cmd, check=True)

print("✅ Database reset complete!")
