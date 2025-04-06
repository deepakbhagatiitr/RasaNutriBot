#!/bin/bash

# Activate virtual environment (if used in Dockerfile)
source /app/venv/bin/activate

# Start Rasa actions server
python -m rasa run actions