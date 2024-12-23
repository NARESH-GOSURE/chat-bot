# Use the official Python image as the base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Set environment variable to ensure Flask listens on all interfaces
ENV FLASK_APP=bot.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=3978 

EXPOSE 3978

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:3978", "bot:app"]

