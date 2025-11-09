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

c = Client()
username = 'reg_test'
password = 'Testpass123'
email = 'reg_test@example.com'
role = 'author'

# Ensure user doesn't exist
User.objects.filter(username=username).delete()

# Register via POST
resp = c.post('/accounts/register/', data={
    'username': username,
    'email': email,
    'password1': password,
    'password2': password,
    'role': role,
}, follow=True, HTTP_HOST='127.0.0.1')
print('Register status:', resp.status_code)
# Debug: show if form errors returned
try:
    form = resp.context.get('form') if resp.context else None
    if form:
        print('Form errors:', form.errors)
    else:
        print('No form in response context; likely redirected.')
except Exception as e:
    print('Could not read response context:', e)

# Check created
exists = User.objects.filter(username=username).exists()
print('User created:', exists)
if exists:
    user = User.objects.get(username=username)
    print('User role:', user.role, 'is_staff:', user.is_staff)

# Attempt login
logged = c.login(username=username, password=password)
print('Logged in:', logged)

# Access author-only page
r = c.get('/post/new/', HTTP_HOST='127.0.0.1')
print('/post/new/ status:', r.status_code)
if r.status_code == 200:
    print('Post create form present')
else:
    print('Redirected or forbidden; status code', r.status_code)
