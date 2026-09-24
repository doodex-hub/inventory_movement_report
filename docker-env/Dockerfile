# Dockerfile — product_history_report, Odoo 20.0 (migrasi 19.0 -> 20.0)
# Docker Hub belum punya image resmi `odoo:20.0` (knowledge/version-diffs/19-to-20.md) -> Odoo dijalankan
# dari source native-target (odoo20) yang di-mount read-only lewat docker-compose.yml; image ini cuma
# menyediakan Python 3.12 + dependency pip Odoo 20 + Google Chrome (Tour test headless, Mode D).
# Resep sama persis dengan project optional_field_save 19->20 (terbukti jalan 2026-09-21).
# requirements.txt = salinan odoo20/requirements.txt (identik).
FROM python:3.12-slim-bookworm

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential python3-dev \
    libpq-dev libldap2-dev libsasl2-dev libxml2-dev libxslt1-dev \
    libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev libffi-dev \
    fonts-dejavu-core fonts-freefont-ttf fonts-noto-core fonts-inconsolata \
    fonts-font-awesome fonts-roboto-unhinted gsfonts \
    postgresql-client \
    wget gnupg ca-certificates \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install --no-cache-dir websocket-client

RUN useradd -ms /bin/bash odoo
USER odoo

ENTRYPOINT ["python3", "/opt/odoo/odoo-bin"]
