import os
import django
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'admin'
email = 'admin@example.com'
password = 'admin'

try:
    if not User.objects.filter(username=username).exists():
        # Create superuser with role='admin' if your custom user model requires it
        # Based on models.py inspection, User has a 'role' field.
        # We should set it to 'admin' just in case, although is_superuser might be enough for Django Admin,
        # the app logic uses the 'role' field.
        User.objects.create_superuser(username=username, email=email, password=password, role='admin')
        print(f"Superuser '{username}' created successfully.")
    else:
        u = User.objects.get(username=username)
        u.set_password(password)
        u.role = 'admin'
        u.is_staff = True
        u.is_superuser = True
        u.save()
        print(f"Superuser '{username}' updated successfully.")
except Exception as e:
    print(f"Error creating superuser: {e}")
