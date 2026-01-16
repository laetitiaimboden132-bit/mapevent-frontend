# 🚀 GUIDE SIMPLE - CLOUDSHELL EN 3 ÉTAPES

## ❌ NE PAS CRÉER D'ENVIRONNEMENT VPC

**Fermez cette fenêtre** - Vous n'en avez pas besoin !

---

## ✅ ÉTAPES SIMPLES

### ÉTAPE 1 : Ouvrir CloudShell Normal

1. Dans la console AWS, **fermez** la fenêtre "Create a VPC environment"
2. Cherchez l'icône **CloudShell** (📱 terminal) dans la **barre d'outils en haut**
3. Cliquez dessus - CloudShell normal s'ouvrira (pas de VPC nécessaire)

---

### ÉTAPE 2 : Créer le script dans CloudShell

**Option A : Copier-coller direct**

1. Une fois CloudShell ouvert, copiez ces commandes une par une :

```bash
cat > creer-layer-cloudshell.sh << 'SCRIPT_EOF'
#!/bin/bash
# Script pour créer Lambda Layer dans AWS CloudShell

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

echo "3. Création du requirements.txt..."
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
# CloudShell a généralement Python 3.9, installons 3.12
if ! command -v python3.12 &> /dev/null; then
    echo "   Installation de Python 3.12..."
    sudo yum install -y python3.12 python3.12-pip -q 2>/dev/null || sudo apt-get install -y python3.12 python3.12-pip -q 2>/dev/null || {
        echo "   Utilisation de Python 3.9 (déjà installé)..."
        PYTHON_VERSION="3.9"
        PYTHON_LIB_PATH="$LAYER_DIR/python/lib/python${PYTHON_VERSION}/site-packages"
        mkdir -p $PYTHON_LIB_PATH
    }
fi

if [ "$PYTHON_VERSION" = "3.12" ]; then
    PYTHON_CMD="python3.12"
    PIP_CMD="python3.12 -m pip"
else
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
fi

echo "5. Mise à jour de pip..."
$PIP_CMD install --upgrade pip -q --user

echo "6. Installation des dépendances Python (Linux)..."
$PIP_CMD install -r /tmp/requirements.txt -t $PYTHON_LIB_PATH --quiet --no-cache-dir --user

echo "7. Nettoyage des fichiers inutiles..."
find $PYTHON_LIB_PATH -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find $PYTHON_LIB_PATH -name "*.pyc" -delete
find $PYTHON_LIB_PATH -name "*.pyo" -delete

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
echo "✅ SUCCES: Lambda Layer créée !"
echo "============================================================"
echo ""
echo "Layer ARN: $LAYER_VERSION"
echo ""
echo "📋 COPIEZ CET ARN (vous en aurez besoin) !"
echo ""
echo "Prochaine étape dans PowerShell local:"
echo "  aws lambda update-function-configuration \\"
echo "    --function-name mapevent-backend \\"
echo "    --layers $LAYER_VERSION \\"
echo "    --region eu-west-1"
echo ""

# Nettoyer
rm -rf $LAYER_DIR

echo "Terminé !"
echo ""
SCRIPT_EOF

chmod +x creer-layer-cloudshell.sh
```

---

### ÉTAPE 3 : Exécuter le script

```bash
./creer-layer-cloudshell.sh
```

**⏱️ Cela prendra 5-10 minutes** (installation des dépendances)

---

## 📋 APRÈS L'EXÉCUTION

Le script affichera quelque chose comme :
```
Layer ARN: arn:aws:lambda:eu-west-1:818127249940:layer:mapevent-python-dependencies:2
```

**COPIEZ CET ARN** !

---

## 🔗 RETOUR À POWERSHELL

Une fois le script terminé dans CloudShell, revenez dans PowerShell et exécutez :

```powershell
# Remplacez :2 par le numéro de version affiché
aws lambda update-function-configuration `
    --function-name mapevent-backend `
    --layers arn:aws:lambda:eu-west-1:818127249940:layer:mapevent-python-dependencies:2 `
    --region eu-west-1
```

Puis testez :
```powershell
.\test-endpoint-suppression.ps1
```

Et supprimez les comptes :
```powershell
.\supprimer-comptes-api.ps1 -Confirm 'OUI'
```

---

## ✅ C'EST TOUT !

**Résumé** :
1. ❌ Fermer la fenêtre VPC
2. ✅ Ouvrir CloudShell normal
3. ✅ Copier-coller les commandes ci-dessus
4. ✅ Exécuter : `./creer-layer-cloudshell.sh`
5. ✅ Copier l'ARN affiché
6. ✅ Attacher la Layer dans PowerShell
7. ✅ Tester et supprimer les comptes

**Facile !** 🚀
