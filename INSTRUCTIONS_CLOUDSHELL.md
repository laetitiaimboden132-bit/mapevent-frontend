# 🚀 CRÉER LAMBDA LAYER AVEC AWS CLOUDSHELL

## ⚡ MÉTHODE LA PLUS SIMPLE ET FONCTIONNELLE

AWS CloudShell est un shell Linux natif dans le cloud AWS, parfait pour créer des Layers avec des binaires Linux.

---

## 📋 ÉTAPES

### 1. Ouvrir AWS CloudShell

1. Connectez-vous à la console AWS : https://console.aws.amazon.com
2. Dans la barre d'outils en haut, cliquez sur l'icône **CloudShell** (symbole de terminal)
3. Attendez que CloudShell se charge (30-60 secondes)

---

### 2. Copier le script dans CloudShell

**Option A : Télécharger le script**
```bash
curl -o creer-layer-cloudshell.sh https://raw.githubusercontent.com/VOTRE_REPO/creer-layer-cloudshell.sh
```

**Option B : Copier-coller le contenu**
1. Ouvrez le fichier `creer-layer-cloudshell.sh` dans votre éditeur local
2. Copiez tout le contenu
3. Dans CloudShell, créez le fichier :
```bash
nano creer-layer-cloudshell.sh
```
4. Collez le contenu (clic droit > Coller)
5. Sauvegardez : `Ctrl+O`, puis `Enter`, puis `Ctrl+X`

---

### 3. Rendre le script exécutable

```bash
chmod +x creer-layer-cloudshell.sh
```

---

### 4. Exécuter le script

```bash
./creer-layer-cloudshell.sh
```

**Durée estimée :** 5-10 minutes (installation des dépendances)

---

### 5. Attacher la Layer à Lambda

Une fois le script terminé, il affichera l'ARN de la Layer (ex: `arn:aws:lambda:eu-west-1:818127249940:layer:mapevent-python-dependencies:2`)

Dans CloudShell, exécutez :

```bash
aws lambda update-function-configuration \
    --function-name mapevent-backend \
    --layers arn:aws:lambda:eu-west-1:818127249940:layer:mapevent-python-dependencies:2 \
    --region eu-west-1
```

**Note :** Remplacez `:2` par le numéro de version créé par le script.

---

### 6. Redéployer Lambda (si nécessaire)

Si votre code Lambda a changé, redéployez-le :

```bash
cd /tmp
# Téléchargez votre code Lambda (ou utilisez git)
# Puis déployez :
aws lambda update-function-code \
    --function-name mapevent-backend \
    --zip-file fileb://votre-code.zip \
    --region eu-west-1
```

---

### 7. Tester l'endpoint

Retournez dans PowerShell local et testez :

```powershell
.\test-endpoint-suppression.ps1
```

Puis, si tout fonctionne :

```powershell
.\supprimer-comptes-api.ps1 -Confirm 'OUI'
```

---

## ✅ AVANTAGES DE CLOUDSHELL

- ✅ **Linux natif** : Binaires Linux garantis
- ✅ **Pas de Docker** : Pas besoin de démarrer Docker Desktop
- ✅ **Pas de WSL2** : Pas de problèmes de timeout
- ✅ **Dans AWS** : Accès direct aux services AWS
- ✅ **Python pré-installé** : Python 3.9 disponible (on peut installer 3.12)

---

## 🔍 DÉPANNAGE

### CloudShell ne démarre pas
- Réessayez après quelques secondes
- Vérifiez votre connexion internet
- Essayez dans un autre navigateur

### Erreur "aws: command not found"
- CloudShell devrait avoir AWS CLI pré-installé
- Si problème, contactez le support AWS

### Erreur lors de la création de la Layer
- Vérifiez que vous êtes dans la bonne région (`eu-west-1`)
- Vérifiez que vous avez les permissions IAM nécessaires

---

## 📝 NOTES

- CloudShell a une limite de 1GB d'espace de stockage
- Les fichiers dans `/tmp` sont supprimés à la fermeture de CloudShell
- CloudShell a un timeout de 20 minutes d'inactivité

---

## 🎯 RÉSUMÉ

1. Ouvrir CloudShell dans AWS Console
2. Copier le script `creer-layer-cloudshell.sh`
3. Exécuter : `./creer-layer-cloudshell.sh`
4. Attacher la Layer à Lambda avec l'ARN affiché
5. Tester l'endpoint de suppression

C'est la méthode la plus simple et la plus fiable ! 🚀
