# Imagen base de Python
FROM python:3.12-slim

# Instalar dependencias del sistema (necesarias para WeasyPrint)
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpango1.0-dev \
    libgdk-pixbuf2.0-0 \
    libgdk-pixbuf2.0-dev \
    shared-mime-info \
    && apt-get clean

# Crear carpeta de la app
WORKDIR /app

# Copiar requerimientos
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Colectar archivos estáticos
RUN python manage.py collectstatic --noinput

# Exponer puerto
EXPOSE 8000

# Comando para iniciar el servidor
CMD ["gunicorn", "maiprot.wsgi:application", "--bind", "0.0.0.0:8000"]
