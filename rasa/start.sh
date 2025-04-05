#!/bin/bash

# PORT=${PORT:-10000}  # fallback to 10000 if PORT is not set
echo "Starting Rasa on Render-assigned port: $PORT"

rasa run --enable-api --cors "*" --debug --port $PORT --host 0.0.0.0
