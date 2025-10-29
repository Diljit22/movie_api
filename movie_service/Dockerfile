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
COPY ./movie_service/src /app/movie_service/

# Create cache directory
RUN mkdir -p /app/.data

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "movie_service.src.movie_api.main:app", "--host", "0.0.0.0", "--port", "8000"]