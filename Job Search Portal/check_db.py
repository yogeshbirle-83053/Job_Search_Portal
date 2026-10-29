import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    django.setup()
    from django.db import connection
    from django.conf import settings

    db_settings = settings.DATABASES['default']
    print("=" * 60)
    print("DJANGO DATABASE CONNECTION CHECK")
    print("=" * 60)
    print(f"Engine  : {db_settings['ENGINE']}")
    print(f"Database: {db_settings['NAME']}")
    print(f"Host    : {db_settings.get('HOST', 'N/A')}")
    print(f"Port    : {db_settings.get('PORT', 'N/A')}")
    print(f"User    : {db_settings.get('USER', 'N/A')}")
    print("-" * 60)

    # Attempt connection
    connection.cursor()
    print("SUCCESS: Connected to database successfully!")
    print("=" * 60)
except Exception as e:
    print(f"ERROR: Could not connect to the database.")
    print(f"Details: {e}")
    print("-" * 60)
    print("Troubleshooting steps:")
    print("1. Ensure MySQL Server is running.")
    print("2. Ensure database exists:")
    print("   mysql -u root -p -e 'CREATE DATABASE job_portal_db CHARACTER SET utf8mb4;'")
    print("3. Check credentials in your .env file (DB_PASSWORD, DB_USER, etc.).")
    print("=" * 60)
    sys.exit(1)
