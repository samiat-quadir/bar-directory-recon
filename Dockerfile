# -----------------------------
# Dockerfile for Bar Directory Recon
# Maintainer: [Your Name/Team]
# Description: Builds a secure, minimal Python 3.13 environment for running Prefect-based automation.
# -----------------------------

# 1. Use official Python slim image for security and efficiency
FROM python:3.13-slim

# 2. Set environment variables for Python best practices
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Set working directory
WORKDIR /app

# 4. Add a non-root user for improved security
RUN adduser --disabled-password appuser
USER appuser

# 5. Install Python dependencies
# Copy only requirements first for better build caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code
COPY . .

# 7. Default command: Run Prefect task
CMD ["prefect", "run", "-p", "src/universal_recon.py"]
