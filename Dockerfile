FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpango1.0-dev \
    libgdk-pixbuf-2.0-0 \
    libgdk-pixbuf-2.0-dev \
    shared-mime-info \
    && apt-get clean

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# Migraciones
RUN python maiprot/manage.py migrate --noinput

# Crear superusuario automáticamente
RUN python maiprot/manage.py shell < maiprot/create_superuser.py

# Static files
RUN python maiprot/manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "maiprot.wsgi:application", "--bind", "0.0.0.0:8000"]
