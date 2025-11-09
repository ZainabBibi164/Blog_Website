# Railway Deployment Guide

## Essential Files
- `Procfile`: Tells Railway how to run your app (uses Gunicorn for production)
- `requirements.txt`: Python dependencies
- `.env.example`: Example environment variables

## Steps to Deploy
1. Push your code to GitHub.
2. Go to [Railway](https://railway.app) and create a new project.
3. Connect your GitHub repo.
4. Set environment variables in Railway dashboard (copy from `.env.example`).
5. Add PostgreSQL plugin for production database.
6. Deploy!

## Static Files
- Add this to your `settings.py`:
```python
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"
MIDDLEWARE = [
    # ...existing middleware...
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # ...existing middleware...
]
```

## Procfile
```
web: gunicorn advanced_blog.wsgi --log-file -
```

## Common Railway Environment Variables
- `DJANGO_SECRET_KEY`: Your Django secret key
- `DJANGO_DEBUG`: Set to `False` for production
- `DJANGO_ALLOWED_HOSTS`: Your Railway app domain
- `DATABASE_URL`: Railway-provided Postgres URL

## Database
- Use Railway's Postgres plugin and set `DATABASE_URL` in your environment variables.

## Extra
- For media files, use S3 or Railway's persistent storage (see Railway docs).
- For custom domains, set `DJANGO_ALLOWED_HOSTS` accordingly.
