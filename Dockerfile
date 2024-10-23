# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies needed for compiling certain packages
RUN apt-get update && apt-get install -y \
    gcc \
    libcairo2-dev \
    libgirepository1.0-dev \
    pkg-config \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install required dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for networking if needed (optional)
EXPOSE 5000

# Command to run your script
CMD ["python", "main.py"]
