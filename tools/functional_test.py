import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','advanced_blog.settings')
import django
django.setup()

from django.test import Client
from apps.accounts.models import User

USERNAME='test_author'
PASSWORD='Testpass123'

# Create user if not exists
user, created = User.objects.get_or_create(username=USERNAME, defaults={'email':'test@example.com','role':'author'})
if created:
    user.set_password(PASSWORD)
    user.save()
    print('Created test user', USERNAME)
else:
    print('Test user exists')

c = Client()
logged = c.login(username=USERNAME, password=PASSWORD)
print('login:', logged)

r = c.get('/post/new/', HTTP_HOST='127.0.0.1')
print('/post/new/ GET ->', r.status_code)

# cleanup not performed
