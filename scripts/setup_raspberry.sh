#!/usr/bin/env bash
set -e

echo "Updating package lists..."
sudo apt update

echo "Installing Python and required tools..."
sudo apt install -y python3 python3-venv python3-pip build-essential portaudio19-dev

echo "Removing old virtual environment..."
rm -rf .venv

echo "Creating virtual environment..."
python3 -m venv .venv

echo "Activating environment..."
source .venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel

echo "Installing dependencies..."
python -m pip install -r requirements.txt

echo "Running program..."
python main.py