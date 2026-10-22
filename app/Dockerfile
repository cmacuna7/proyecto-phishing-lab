FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY labapp ./labapp
COPY wsgi.py .

# Usuario sin privilegios; los directorios de datos y logs se montan como volúmenes.
RUN useradd --uid 1000 --create-home app \
    && mkdir -p /var/log/lab-app /var/lib/lab-app \
    && chown -R app:app /var/log/lab-app /var/lib/lab-app
USER app

EXPOSE 8000
# UN solo worker (con hilos): el barrido de bloqueos y el contador viven en este proceso.
CMD ["gunicorn", "--workers", "1", "--threads", "4", "--bind", "0.0.0.0:8000", "wsgi:app"]
