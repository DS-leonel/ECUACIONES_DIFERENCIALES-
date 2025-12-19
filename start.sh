#!/bin/bash

# Activar entorno virtual si lo tienes
# source venv/bin/activate  # Descomenta si usas venv

# Instalar dependencias (opcional, pero recomendado)
pip install -r requirements.txt

# Ejecutar la app con Gunicorn
gunicorn main_app:app --bind 0.0.0.0:$PORT
