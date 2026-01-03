#!/bin/bash
# Script de déploiement Lambda pour MapEventAI Backend

set -e

echo "🚀 Déploiement Lambda MapEventAI Backend..."

# Variables
FUNCTION_NAME="mapevent-backend"
REGION="eu-west-1"
ZIP_FILE="lambda-deploy.zip"

# Nettoyer les anciens fichiers
echo "🧹 Nettoyage..."
rm -f $ZIP_FILE
rm -rf __pycache__ *.pyc
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Installer les dépendances dans un dossier local
echo "📦 Installation des dépendances..."
pip install -r backend/requirements.txt -t . --upgrade --quiet

# Créer le fichier ZIP
echo "📦 Création du package..."
zip -r $ZIP_FILE . -x "*.git*" -x "*.pyc" -x "__pycache__/*" -x "*.zip" -x "deploy.sh" -x "test_*.py" -x "*.md" > /dev/null

# Vérifier la taille du package (Lambda limite à 250MB décompressé, 50MB compressé)
SIZE=$(du -m $ZIP_FILE | cut -f1)
if [ $SIZE -gt 50 ]; then
    echo "⚠️  Attention: Le package fait ${SIZE}MB (limite: 50MB)"
fi

# Déployer sur Lambda
echo "☁️  Déploiement sur AWS Lambda..."
aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://$ZIP_FILE \
    --region $REGION

# Attendre que le déploiement soit terminé
echo "⏳ Attente de la mise à jour..."
aws lambda wait function-updated \
    --function-name $FUNCTION_NAME \
    --region $REGION

echo "✅ Déploiement terminé avec succès!"
echo "📊 Informations de la fonction:"
aws lambda get-function \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --query 'Configuration.[FunctionName,Runtime,LastModified,CodeSize]' \
    --output table





