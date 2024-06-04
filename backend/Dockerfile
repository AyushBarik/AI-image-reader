# Use the official Python image from the Docker Hub
FROM python:3.11-slim-bullseye

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file (if you have one)
COPY requirements.txt .

# Install the dependencies specified in requirements.txt
RUN pip install .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code
COPY . .

# Define the command to run the script
CMD ["python","pres/test.py"]
