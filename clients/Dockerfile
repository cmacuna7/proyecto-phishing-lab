# "Equipo de usuario" del laboratorio: Python + herramientas para ejecutar los escenarios.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir requests "qrcode[pil]" \
    && apt-get update && apt-get install -y --no-install-recommends curl iputils-ping \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /lab
CMD ["sleep", "infinity"]
