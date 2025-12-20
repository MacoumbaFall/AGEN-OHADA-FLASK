FROM python:3.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP wsgi.py
ENV FLASK_ENV production

# Install system dependencies
# These are required by WeasyPrint (Pango, Cairo, etc.) and Psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libffi-dev \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libjpeg-dev \
    libopenjp2-7-dev \
    shared-mime-info \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port (Koyeb defaults to 8000 but we can specify)
EXPOSE 8000

# Start GSunicorn
# Note: we use wsgi:application because that's what is defined in wsgi.py
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:application"]
