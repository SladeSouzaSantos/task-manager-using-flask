# Dockerfile for Task Manager Flask application
# Use a lightweight Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies (if any) and clean up
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a working directory
# Set the working directory to the inner Flask project where the code lives
WORKDIR /app/todo_project

# Copy only requirements first for caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code
COPY . ./

# Expose the Flask default port
EXPOSE 5000

# Run the application using the project's entry point (ensures DB init)
CMD ["python", "run.py"]
