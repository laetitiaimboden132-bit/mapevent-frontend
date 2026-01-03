# ☁️ CloudFront - Méthode Simple (Étape par Étape)

## 🎯 Objectif
Rendre `https://mapevent.world` accessible en 4 étapes simples.

---

## 📋 ÉTAPE 1 : Créer le Bucket S3 (5 min)

1. **AWS Console** → Chercher **"S3"**
2. **Créer un bucket**
3. **Remplir** :
   - **Nom du bucket** : `mapevent-world` (doit être unique globalement)
   - **Région** : `eu-west-1` (ou votre région préférée)
   - **Bloquer l'accès public** : **DÉSACTIVÉ** ✅
   - **Hébergement de site web statique** : **ACTIVÉ** ✅
   - **Créer**

4. **Uploader les fichiers** :
   - Cliquer sur le bucket
   - **Téléverser** (Upload)
   - Sélectionner TOUS les fichiers du dossier `public/` :
     - `mapevent.html`
     - `map_logic.js`
     - Dossier `assets/` (tout le contenu)
     - Dossier `trees/` (tout le contenu)
     - Tous les autres fichiers
   - **Téléverser**

5. **Permissions** :
   - **Autorisations** → **Politique de bucket** → **Modifier**
   - Coller cette politique (remplacer `mapevent-world` par votre nom de bucket) :
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": "*",
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::mapevent-world/*"
       }
     ]
   }
   ```
   - **Enregistrer**

✅ **Étape 1 terminée !**

---

## 📋 ÉTAPE 2 : Créer CloudFront (10 min)

1. **AWS Console** → Chercher **"CloudFront"**
2. **Créer une distribution**

3. **Origine** :
   - **Origine du domaine** : Cliquer → Sélectionner votre bucket S3
     - Ex: `mapevent-world.s3.eu-west-1.amazonaws.com`
   - **Nom de l'origine** : `mapevent-world-s3`
   - **Origine de l'accès** : **Origine de l'accès public (OAI)**
     - Cliquer sur **Créer une origine de l'accès d'identité**
     - **Nom** : `mapevent-world-oai`
     - **Créer**
   - **Bucket** : Sélectionner votre bucket

4. **Comportements par défaut** :
   - Laisser les valeurs par défaut
   - **Viewer protocol policy** : **Redirect HTTP to HTTPS** ✅

5. **Paramètres du visualiseur** :
   - **Alternate domain names (CNAMEs)** :
     - Cliquer **Ajouter un élément**
     - Ajouter : `mapevent.world`
   - **SSL certificate** :
     - **Custom SSL certificate**
     - Sélectionner : `mapevent.world (33d9e586-7c47-4d6a-8e83-4bbad4252595)`

6. **Paramètres par défaut** :
   - **Default root object** : `mapevent.html` ✅

7. **Créer une distribution**
   - ⏱️ **Attendre 5-15 minutes** (statut = "Déployé")

✅ **Étape 2 terminée !**

---

## 📋 ÉTAPE 3 : Configurer Route 53 (2 min)

**ATTENDRE** que CloudFront soit "Déployé" avant de continuer !

1. **AWS Console** → **Route 53**
2. **Hosted zones** → Cliquer sur `mapevent.world`
3. **Créer un enregistrement**
4. **Remplir** :
   - **Nom de l'enregistrement** : Laisser vide (pour `mapevent.world`)
   - **Type** : **A - Routes le trafic vers une ressource AWS**
   - **Alias** : **Oui** ✅
   - **Route le trafic vers** :
     - **Alias vers une distribution CloudFront**
     - Sélectionner votre distribution
   - **Créer des enregistrements**

✅ **Étape 3 terminée !**

---

## 📋 ÉTAPE 4 : Attendre et Tester (15-30 min)

1. **Attendre 15-30 minutes** pour la propagation DNS
2. **Tester** :
   - Ouvrir : `https://mapevent.world`
   - OU : `https://mapevent.world/mapevent.html`

✅ **Terminé !**

---

## 🐛 Si ça ne marche pas

### Vérifier CloudFront :
- Statut = "Déployé" ?
- Domain name CloudFront fonctionne ? (ex: `d1234567890.cloudfront.net`)

### Vérifier Route 53 :
- Enregistrement A (Alias) existe ?
- Pointe vers la bonne distribution CloudFront ?

### Vérifier S3 :
- Tous les fichiers sont uploadés ?
- Permissions OK ?

---

## ✅ Checklist Rapide

- [ ] Bucket S3 créé et fichiers uploadés
- [ ] CloudFront créé avec CNAME `mapevent.world`
- [ ] Certificat ACM sélectionné
- [ ] CloudFront déployé (statut = "Déployé")
- [ ] Route 53 : Enregistrement A créé
- [ ] Attendu 15-30 minutes
- [ ] Test : `https://mapevent.world` fonctionne

---

**C'est tout ! Simple et rapide. 🚀**


