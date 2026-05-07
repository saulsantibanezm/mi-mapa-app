#!/bin/bash
# Script para instalar el proyecto en cualquier computadora

echo "📦 Instalando Mapa de México..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no está instalado"
    exit 1
fi

# Crear entorno virtual
python3 -m venv venv

# Activar
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

echo "✅ Instalación completa"
echo ""
echo "Para ejecutar: ./run.sh"
