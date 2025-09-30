FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set environment variables (e.g., for Flask app)
ENV FLASK_APP=flask_server.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose the port the app will run on
EXPOSE 5000

# Run the app using gunicorn
CMD ["gunicorn", "flask_server:server"]
