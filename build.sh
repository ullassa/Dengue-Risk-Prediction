#!/usr/bin/env bash
# build.sh - Render build script

set -o errexit  # exit on error

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database and create admin user
python init_db.py
echo "Initializing database..."
python init_db.py

echo "Build completed successfully!"
