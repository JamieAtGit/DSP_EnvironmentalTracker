# Use a Python base
FROM python:3.10-slim

# Set environment vars
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (including Chromium for scraping)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    chromium-driver \
    chromium \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libasound2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxi6 \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r ../../requirements.txt

# Expose port
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
