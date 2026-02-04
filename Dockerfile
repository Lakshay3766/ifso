# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make the script executable (optional, since we're using python)
# RUN chmod +x cdr_uploader.py

# Define the command to run the application
CMD ["python", "cdr_uploader.py"]