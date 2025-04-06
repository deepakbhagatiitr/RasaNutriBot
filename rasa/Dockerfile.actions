# Use the Rasa SDK image as the base
FROM rasa/rasa-sdk:3.6.2

# Switch to root to install system dependencies and ensure permissions
USER root

# Update package lists and install build tools, including Cython and libyaml-dev
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libyaml-dev \
    cython3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy action files and entrypoint
COPY ./actions /app/actions
COPY entrypoint.sh /app/entrypoint.sh

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Create virtual environment
RUN python3 -m venv /app/venv

# Upgrade pip, setuptools, and wheel in the virtual environment
RUN /app/venv/bin/pip install --upgrade pip setuptools wheel cython

# Install Rasa and other dependencies in the virtual environment
RUN /app/venv/bin/pip install --no-cache-dir rasa==3.6.21 numpy==1.23.5 spacy requests

# Download spaCy model in the virtual environment
RUN /app/venv/bin/python3 -m spacy download en_core_web_sm

# Set environment variables as specified in Docker Compose
ENV PYTHONPATH=/app

# Switch back to non-root user (if required by the base image)
USER 1001

# Set ENTRYPOINT to use the virtual environment and execute the action server
ENTRYPOINT ["/app/venv/bin/python", "-m", "rasa", "run", "actions"]
