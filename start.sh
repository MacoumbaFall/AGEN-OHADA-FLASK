#!/bin/sh
# Start script for Koyeb/Render/Docker

echo "Running migrations..."
flask db upgrade

echo "Starting Gunicorn..."
# Use PORT from environment or default to 8000
gunicorn -b 0.0.0.0:${PORT:-8000} wsgi:application
