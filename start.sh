#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(phone='+998901234567').exists():
    User.objects.create_superuser(phone='+998901234567', password='admin123')
    print('Superuser created: +998901234567 / admin123')
else:
    print('Superuser already exists')
"

# Start development server
python manage.py runserver 0.0.0.0:8000
