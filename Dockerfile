# Use the official Python 3.9 image as base
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory (containing code and requirements.txt) to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 to the outside world
# EXPOSE 8000

# Command to run the FastAPI application using uvicorn
CMD ["python", "app.py"]

