FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY ./pyproject.toml /app/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e ".[dev]"

# Copy the application code
COPY ./user_service/src /app/user_service/src

# Create a directory for any persistent data, like JSON files
RUN mkdir -p /app/.data

# Expose the port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "user_service.src.user_api.main:app", "--host", "0.0.0.0", "--port", "8001"]