FROM python:3.6-stretch

WORKDIR /app

EXPOSE 8000

# sets the environment variable
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=core.settings \
    PORT=8000 \
    WEB_CONCURRENCY=3

# Install operating system dependencies.
RUN apt-get update -y && \
    apt-get install -y apt-transport-https rsync gettext libgettextpo-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python requirements.
COPY requirements.txt requirements.txt ./
RUN pip install -r requirements.txt

# Copy application code.
COPY . .

# Install assets
# RUN python manage.py collectstatic --noinput

# Run application
CMD gunicorn config.wsgi:application