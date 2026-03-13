#!/usr/bin/env bash
set -e

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing dependencies..."
python -m pip install -r requirements.txt

echo "Running program..."
python main.py