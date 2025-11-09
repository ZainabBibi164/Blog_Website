import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so `advanced_blog` package can be imported
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE','advanced_blog.settings')
django.setup()

from django.urls import resolve, Resolver404

paths = ['/','/post/new/','/post/some-slug/','/accounts/profile/']
for p in paths:
    try:
        match = resolve(p)
        print(p, '->', match.view_name, match.func.__name__)
    except Resolver404:
        print(p, '-> NOT FOUND')
