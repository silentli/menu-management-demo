#!/bin/sh

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z -w 1 $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
  echo "Still waiting for PostgreSQL..."
done
echo "PostgreSQL is up and running!"

# Create and apply migrations
echo "Creating migrations..."
python manage.py makemigrations

echo "Applying migrations..."
python manage.py migrate

# Load initial data
echo "Loading initial data..."
python manage.py load_initial_data

# Create superuser
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created.')
else:
    print('Superuser already exists.')
"

# Run the command provided as arguments to this script
exec "$@" 