#!/bin/bash
set -e

# Variables
LAYER_DIR="/tmp/lambda-layer-build"
PYTHON_VER="3.12"
PYTHON_LIB_PATH="$LAYER_DIR/python/lib/python$PYTHON_VER/site-packages"

echo "Creation de la structure Lambda Layer..."
mkdir -p $PYTHON_LIB_PATH

echo "Installation de Python $PYTHON_VER si necessaire..."
if ! command -v python3.12 &> /dev/null; then
    echo "Installation de Python 3.12..."
    sudo apt-get update -qq
    sudo apt-get install -y python3.12 python3.12-venv python3-pip -qq
fi

echo "Installation des dependances Python (Linux)..."
python3.12 -m pip install --upgrade pip -q
python3.12 -m pip install -r /mnt/c/MapEventAI_NEW/frontend/lambda-package/backend/requirements.txt -t $PYTHON_LIB_PATH --quiet --no-cache-dir

echo "Nettoyage des fichiers inutiles..."
find $PYTHON_LIB_PATH -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find $PYTHON_LIB_PATH -name "*.pyc" -delete
find $PYTHON_LIB_PATH -name "*.pyo" -delete
find $PYTHON_LIB_PATH -name "*.dist-info" -type d -exec rm -r {} + 2>/dev/null || true

echo "Creation du ZIP de la Layer..."
cd $LAYER_DIR
zip -r /mnt/c/MapEventAI_NEW/frontend/lambda-package/lambda-layer-wsl2.zip python/ -q

echo "Nettoyage..."
rm -rf $LAYER_DIR

echo "SUCCES: Lambda Layer creee dans lambda-layer-wsl2.zip"