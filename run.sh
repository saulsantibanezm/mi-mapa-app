#!/bin/bash
# Script para ejecutar el proyecto fácilmente

echo "🚀 Iniciando Mapa de México..."

# Activar entorno virtual
source venv/bin/activate

# Ejecutar la aplicación
uvicorn main:app --reload --host 127.0.0.1 --port 8000
