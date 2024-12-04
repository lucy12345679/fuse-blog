# Use the official Python image as the base
FROM python:3.9-slim

# Set environment variables to disable Python output buffering and avoid bytecode files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire project into the container
COPY . /app/

# Expose the application port
EXPOSE 8000

# Define the command to run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
