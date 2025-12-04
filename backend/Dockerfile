# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY src src

# Expose port 5000
EXPOSE 5000

# Define environment variable
ENV MODULE_NAME="src.api.main"
ENV VARIABLE_NAME="app"
ENV PORT="5000"

# Run app.py when the container launches
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "5000"]
