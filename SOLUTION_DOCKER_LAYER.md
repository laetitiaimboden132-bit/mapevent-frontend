# 🐳 SOLUTION : Utiliser Docker pour créer la Lambda Layer

## 🎯 Problème

Même avec `--platform manylinux2014_x86_64`, pip installe parfois des binaires Windows au lieu de Linux. **La solution la plus fiable est d'utiliser Docker pour installer les dépendances sur Linux**.

## ✅ Solution : Docker pour Lambda Layer

### Étape 1 : Installer Docker Desktop (si pas déjà installé)

1. Téléchargez Docker Desktop : https://www.docker.com/products/docker-desktop
2. Installez et démarrez Docker Desktop
3. Vérifiez : `docker --version`

### Étape 2 : Créer un Dockerfile pour Lambda Layer

J'ai créé `Dockerfile.lambda-layer` qui :
- Utilise une image Python Linux officielle
- Installe toutes les dépendances pour Linux
- Crée la structure Lambda Layer correcte
- Exporte le package ZIP

### Étape 3 : Construire la Layer avec Docker

```bash
docker build -f Dockerfile.lambda-layer -t lambda-layer-builder .
docker run --rm -v ${PWD}/lambda-package:/output lambda-layer-builder
```

### Étape 4 : Publier la Layer

```bash
aws lambda publish-layer-version \
  --layer-name mapevent-python-dependencies \
  --zip-file fileb://python-layer.zip \
  --compatible-runtimes python3.12 \
  --region eu-west-1
```

---

## 🔄 Solution Alternative : Utiliser une VM Linux temporaire

Si Docker n'est pas disponible, vous pouvez :
1. Créer une EC2 instance Linux temporaire
2. Installer Python et pip
3. Exécuter le script d'installation des dépendances
4. Télécharger le ZIP créé
5. Publier la Layer depuis votre machine

---

## 🎯 Résumé

**Pour créer une Lambda Layer avec des binaires Linux :**
1. **Utiliser Docker** (recommandé)
2. **OU utiliser une VM Linux** (EC2, WSL2, etc.)
3. **OU utiliser GitHub Actions** (automatisation CI/CD)

**Installation sur Windows ne garantit pas les binaires Linux.**

