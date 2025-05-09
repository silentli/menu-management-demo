FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Collect static files
RUN mkdir -p staticfiles
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]

# Run the application
CMD ["gunicorn", "menu_management.wsgi:application", "--bind", "0.0.0.0:8000"] 