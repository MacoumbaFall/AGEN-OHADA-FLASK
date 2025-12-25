FROM python:3.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP wsgi.py
ENV FLASK_ENV production

# Install system dependencies
# Added libxml2-dev and libxslt1-dev for lxml (required by python-docx-template)
# Added fontconfig and other libs for WeasyPrint/xhtml2pdf
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libffi-dev \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libharfbuzz0b \
    libjpeg-dev \
    libopenjp2-7-dev \
    shared-mime-info \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    fontconfig \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Create and set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --verbose

# Copy project files
COPY . .

# Expose port (Koyeb usually expects 8000)
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:application"]
