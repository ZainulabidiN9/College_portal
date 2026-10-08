# College Portal

Django-based academic portal for students, teachers, and administrators.

## Local development

```sh
python manage.py migrate
python manage.py runserver
```

## Tests

```sh
python manage.py test
```

## Deploy on Render

The repository includes a Render Blueprint in `render.yaml`. In Render, create a new Blueprint and connect this GitHub repository. Before the web service starts, create a persistent PostgreSQL database and set its internal connection URL as the service's `DATABASE_URL` environment variable. The Blueprint generates `DJANGO_SECRET_KEY`; production settings reject missing secrets or database URLs.

The build installs `requirements.txt` and collects static files. The start command applies database migrations and runs Gunicorn. To enable email delivery, also set `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, and `EMAIL_USE_TLS` to the values from your SMTP provider.

The web service is configured for Render's free web tier, which may spin down when idle. Choose a persistent PostgreSQL plan appropriate for the student records and review Render's current pricing and retention terms before provisioning it.
