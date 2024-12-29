# Use official Python runtime as base image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    vim \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY ./requirements.lock /app/


# Install dependencies
RUN sed '/-e /d' requirements.lock > requirements.txt && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PORT=8000

# Expose port
EXPOSE 8000

# Run uvicorn server
CMD ["python", "-m", "uvicorn", "youtube_search.web:app", "--host", "0.0.0.0", "--port", "8000"] 