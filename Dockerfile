# Use Python 3.13 slim image for improved security and efficiency
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
WORKDIR /app

# Add a non-root user for security
RUN adduser --disabled-password appuser
USER appuser

# Install dependencies with no-cache for security
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Replace CMD with Prefect task execution
CMD ["prefect", "run", "-p", "src/universal_recon.py"]
