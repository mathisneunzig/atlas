#!/usr/bin/env bash
set -e

echo "Removing old virtual environment..."
rm -rf .venv

echo "Creating new virtual environment..."
python3 -m venv .venv

echo "Activating environment..."
source .venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel

echo "Installing dependencies..."
python -m pip install -r requirements.txt