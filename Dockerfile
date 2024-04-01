# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt /app/

# Install Flask and other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY app.py /app/

# Expose port 5000
EXPOSE 5000

# Command to run the Flask application
CMD ["flask", "run", "--host", "0.0.0.0"]
