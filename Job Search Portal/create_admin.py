import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = "admin"
email = "admin@jobportal.com"
password = "AdminPassword@123"

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        role=User.ROLE_ADMIN
    )
    print(f"Superuser '{username}' created successfully!")
else:
    print(f"Superuser '{username}' already exists.")
