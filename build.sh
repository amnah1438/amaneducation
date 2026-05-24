#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Load data from local database dump (only if database is empty)
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if User.objects.count() <= 1:
    import subprocess
    subprocess.run(['python', 'manage.py', 'loaddata', 'data_dump.json'], check=True)
    print('Data loaded successfully!')
else:
    print('Data already exists, skipping load.')
"
