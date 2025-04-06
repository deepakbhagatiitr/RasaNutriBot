#!/bin/bash

# Set a default port if none provided by Render
PORT=${PORT:-5005}

echo "Starting Rasa on Render-assigned port: $PORT"
rasa run --enable-api --cors "*" --host 127.0.0.1 --port $PORT



