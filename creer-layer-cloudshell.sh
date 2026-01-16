#!/bin/bash
# Script pour créer Lambda Layer dans AWS CloudShell
# Copiez ce script dans CloudShell et exécutez-le

set -e

echo "============================================================"
echo "CREATION LAMBDA LAYER DANS AWS CLOUDSHELL"
echo "============================================================"
echo ""

# Variables
LAYER_NAME="mapevent-python-dependencies"
REGION="eu-west-1"
PYTHON_VERSION="3.12"
LAYER_DIR="/tmp/lambda-layer-build"
PYTHON_LIB_PATH="$LAYER_DIR/python/lib/python${PYTHON_VERSION}/site-packages"

echo "1. Nettoyage..."
rm -rf $LAYER_DIR
rm -f /tmp/python-layer.zip

echo "2. Création de la structure Lambda Layer..."
mkdir -p $PYTHON_LIB_PATH

echo "3. Téléchargement de requirements.txt depuis GitHub ou création..."
# Créer un requirements.txt minimal si nécessaire
cat > /tmp/requirements.txt << 'EOF'
flask==3.0.0
flask-cors==4.0.0
werkzeug==3.1.4
bcrypt==4.1.2
psycopg2-binary==2.9.9
requests==2.31.0
boto3==1.34.0
python-jose[cryptography]==3.3.0
pyjwt==2.8.0
stripe==7.8.0
sendgrid==6.11.0
Pillow==10.2.0
redis==5.0.1
google-cloud-vision==3.4.5
EOF

echo "4. Installation de Python $PYTHON_VERSION si nécessaire..."
if ! command -v python3.12 &> /dev/null; then
    echo "   Installation de Python 3.12..."
    sudo yum install -y python3.12 python3.12-pip -q || sudo apt-get install -y python3.12 python3.12-pip -q
fi

echo "5. Mise à jour de pip..."
python3.12 -m pip install --upgrade pip -q

echo "6. Installation des dépendances Python (Linux)..."
python3.12 -m pip install -r /tmp/requirements.txt -t $PYTHON_LIB_PATH --quiet --no-cache-dir

echo "7. Nettoyage des fichiers inutiles..."
find $PYTHON_LIB_PATH -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find $PYTHON_LIB_PATH -name "*.pyc" -delete
find $PYTHON_LIB_PATH -name "*.pyo" -delete
find $PYTHON_LIB_PATH -name "*.dist-info" -type d -exec rm -r {} + 2>/dev/null || true

echo "8. Création du ZIP de la Layer..."
cd $LAYER_DIR
zip -r /tmp/python-layer.zip python/ -q

echo "9. Vérification de la taille..."
SIZE=$(du -h /tmp/python-layer.zip | cut -f1)
echo "   Taille: $SIZE"

echo "10. Publication de la Layer sur AWS..."
LAYER_VERSION=$(aws lambda publish-layer-version \
    --layer-name $LAYER_NAME \
    --zip-file fileb:///tmp/python-layer.zip \
    --compatible-runtimes "python${PYTHON_VERSION}" \
    --compatible-architectures x86_64 \
    --description "Dépendances Python pour MapEventAI (Linux - via CloudShell)" \
    --region $REGION \
    --query 'LayerVersionArn' \
    --output text)

echo ""
echo "============================================================"
echo "SUCCES: Lambda Layer créée !"
echo "============================================================"
echo ""
echo "Layer ARN: $LAYER_VERSION"
echo ""
echo "Prochaine étape: Attacher cette Layer à Lambda"
echo "  aws lambda update-function-configuration \\"
echo "    --function-name mapevent-backend \\"
echo "    --layers $LAYER_VERSION \\"
echo "    --region $REGION"
echo ""

# Nettoyer
rm -rf $LAYER_DIR

echo "Terminé !"
echo ""
