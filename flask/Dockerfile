# Use the official Python image from the Docker Hub as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the local app directory contents into the container at /app
COPY . /app

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 to allow external access to the Flask app
EXPOSE 5000

# Run the Flask app on container start
CMD ["python", "app.py"]
