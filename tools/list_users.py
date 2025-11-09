import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','advanced_blog.settings')
import django
django.setup()

from apps.accounts.models import User

print('Users in DB:')
for u in User.objects.all():
    print('-', u.username, '| role=', u.role, '| is_staff=', u.is_staff, '| is_active=', u.is_active)
