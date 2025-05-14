# Set context to backend/, but copy the full project
FROM python:3.11-slim

# Set working dir
WORKDIR /app

# Copy everything from root (adjust context in Render if needed)
COPY ../ /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the app
CMD ["gunicorn", "api.app:app", "--bind", "0.0.0.0:5000"]
