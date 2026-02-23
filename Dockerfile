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

# Note: This project is a Tkinter GUI app. Running the GUI inside Docker requires
# additional setup (Tk libraries + display forwarding). For local usage, prefer:
#   python3 main.py

# Define the default command (kept for completeness)
CMD ["python", "main.py"]
