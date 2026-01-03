# ☁️ Configurer CloudFront pour mapevent.world

## 🎯 Objectif

Rendre le site accessible via `https://mapevent.world` en utilisant CloudFront avec le certificat ACM validé.

---

## 📋 Étape 1 : Préparer les fichiers (S3 ou autre source)

### Option A : Utiliser S3 (Recommandé)

1. **Créer un bucket S3** :
   - AWS Console → **S3**
   - **Créer un bucket**
   - **Nom** : `mapevent-world-static` (ou similaire)
   - **Région** : `eu-west-1` (ou votre région préférée)
   - **Bloquer l'accès public** : DÉSACTIVÉ (pour CloudFront)
   - **Créer**

2. **Activer l'hébergement de site web statique** :
   - Dans le bucket → **Propriétés**
   - **Hébergement de site web statique** → **Modifier**
   - **Activer** → **Enregistrer**

3. **Uploader les fichiers** :
   - Aller dans le bucket
   - **Téléverser** (Upload)
   - Uploader tous les fichiers du dossier `public/` :
     - `mapevent.html`
     - `map_logic.js`
     - `assets/` (dossier complet)
     - `trees/` (dossier complet)
     - Tous les autres fichiers nécessaires

4. **Configurer les permissions** :
   - **Autorisations** → **Politique de bucket**
   - Ajouter cette politique (remplacer `BUCKET_NAME` par le nom de votre bucket) :
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "PublicReadGetObject",
         "Effect": "Allow",
         "Principal": "*",
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::BUCKET_NAME/*"
       }
     ]
   }
   ```

### Option B : Utiliser un serveur HTTP existant

Si vous avez déjà un serveur qui héberge les fichiers, notez son URL (ex: `http://votre-serveur.com`).

---

## 📋 Étape 2 : Créer la distribution CloudFront

1. **Aller dans CloudFront** :
   - AWS Console → **CloudFront**
   - **Créer une distribution**

2. **Configurer l'origine** :

   **Si vous utilisez S3** :
   - **Origine du domaine** :
     - Cliquer sur le champ
     - Sélectionner votre bucket S3 (ex: `mapevent-world-static.s3.eu-west-1.amazonaws.com`)
     - OU utiliser le nom du bucket directement (ex: `mapevent-world-static`)
   - **Nom de l'origine** : `mapevent-world-s3` (ou similaire)
   - **Origine de l'accès** : **Origine de l'accès public (OAI)** (recommandé)
     - Cliquer sur **Créer une origine de l'accès d'identité**
     - **Nom** : `mapevent-world-oai`
     - **Créer**
   - **Bucket** : Sélectionner votre bucket

   **Si vous utilisez un serveur HTTP** :
   - **Origine du domaine** : Votre URL (ex: `http://votre-serveur.com`)
   - **Nom de l'origine** : `mapevent-world-server`
   - **Protocole** : HTTP ou HTTPS selon votre serveur

3. **Configurer les comportements par défaut** :
   - **Chemins d'accès** : `*` (tous les chemins)
   - **Méthodes HTTP autorisées** : `GET, HEAD, OPTIONS`
   - **Cache policy** : `CachingOptimized` (ou `CachingDisabled` pour le développement)
   - **Origin request policy** : `CORS-S3Origin` (si vous utilisez S3)
   - **Viewer protocol policy** : **Redirect HTTP to HTTPS** (important !)

4. **Configurer les paramètres du visualiseur** :
   - **Price class** : `Use all edge locations` (ou `Use only North America and Europe` pour économiser)
   - **Alternate domain names (CNAMEs)** :
     - Cliquer sur **Ajouter un élément**
     - Ajouter : `mapevent.world`
     - Ajouter : `www.mapevent.world` (optionnel)
   - **SSL certificate** :
     - **Custom SSL certificate** → Sélectionner votre certificat ACM
     - Le certificat doit être dans la région **us-east-1** (N. Virginia)
     - Vous devriez voir : `mapevent.world (33d9e586-7c47-4d6a-8e83-4bbad4252595)`

5. **Configurer les paramètres par défaut** :
   - **Default root object** : `mapevent.html` (important !)
   - **Compression automatique** : **Oui** (recommandé)
   - **Commentaire** : `Distribution pour mapevent.world`

6. **Créer la distribution** :
   - Cliquer sur **Créer une distribution**
   - ⏱️ **Attendre 5-15 minutes** pour que la distribution soit déployée

---

## 📋 Étape 3 : Configurer Route 53

Une fois que CloudFront est déployé (statut = "Déployé") :

1. **Aller dans Route 53** :
   - AWS Console → **Route 53**
   - **Hosted zones** → Cliquer sur `mapevent.world`

2. **Créer un enregistrement A (Alias)** :
   - **Créer un enregistrement**
   - **Nom de l'enregistrement** : Laissez vide (pour `mapevent.world`) OU `www` (pour `www.mapevent.world`)
   - **Type** : **A - Routes le trafic vers une ressource AWS**
   - **Alias** : **Oui**
   - **Route le trafic vers** :
     - **Alias vers une distribution CloudFront**
     - Sélectionner votre distribution CloudFront
     - OU coller le **Domain name CloudFront** (ex: `d1234567890.cloudfront.net`)
   - **Type d'enregistrement d'évaluation** : **A**
   - **TTL** : Laisser par défaut
   - **Créer des enregistrements**

3. **Vérifier les enregistrements** :
   - Vous devriez voir dans Route 53 :
     ```
     mapevent.world  A  Alias  d1234567890.cloudfront.net
     ```

---

## ⏱️ Étape 4 : Attendre la propagation

1. **CloudFront** : 5-15 minutes pour le déploiement
2. **DNS** : 5-30 minutes pour la propagation
3. **Total** : Environ 15-45 minutes

---

## ✅ Étape 5 : Tester

1. **Vérifier CloudFront** :
   - CloudFront → Votre distribution
   - **Statut** doit être **"Déployé"**
   - **Domain name** : Notez cette URL (ex: `d1234567890.cloudfront.net`)

2. **Tester avec le domaine CloudFront** :
   - Ouvrir : `https://d1234567890.cloudfront.net/mapevent.html`
   - Le site devrait s'afficher

3. **Tester avec mapevent.world** :
   - Attendre 15-30 minutes après la configuration Route 53
   - Ouvrir : `https://mapevent.world/mapevent.html`
   - OU simplement : `https://mapevent.world` (si default root object est configuré)

---

## 🐛 Dépannage

### Problème 1 : "Access Denied" depuis CloudFront

**Solution** :
- Vérifier les permissions S3 (politique de bucket)
- Vérifier que l'OAI est correctement configurée
- Vérifier que le bucket autorise l'accès depuis CloudFront

### Problème 2 : Le site ne s'affiche pas avec mapevent.world

**Vérifier** :
1. Route 53 → Vérifier que l'enregistrement A (Alias) existe
2. CloudFront → Vérifier que `mapevent.world` est dans "Alternate domain names"
3. CloudFront → Vérifier que le certificat ACM est sélectionné
4. Attendre la propagation DNS (peut prendre jusqu'à 48h, mais généralement 5-30 min)

### Problème 3 : Erreur SSL "Certificate not found"

**Solution** :
- Vérifier que le certificat ACM est dans la région **us-east-1**
- Vérifier que le certificat est **"Émis"** (pas "En attente")
- Vérifier que `mapevent.world` est dans les domaines du certificat

### Problème 4 : Le site charge mais les assets ne s'affichent pas

**Solution** :
- Vérifier que tous les fichiers sont uploadés dans S3
- Vérifier les chemins dans `map_logic.js` (doivent être relatifs)
- Vérifier les permissions S3

---

## 📋 Checklist

- [ ] Bucket S3 créé et fichiers uploadés (ou serveur HTTP configuré)
- [ ] Distribution CloudFront créée
- [ ] Origine configurée (S3 ou serveur HTTP)
- [ ] Alternate domain names : `mapevent.world` ajouté
- [ ] Certificat ACM sélectionné dans CloudFront
- [ ] Default root object : `mapevent.html`
- [ ] Distribution CloudFront déployée (statut = "Déployé")
- [ ] Enregistrement A (Alias) créé dans Route 53
- [ ] Test avec le domaine CloudFront : OK
- [ ] Test avec mapevent.world : OK

---

## 🎯 Résumé des Actions

1. **S3** : Créer bucket → Upload fichiers → Configurer permissions
2. **CloudFront** : Créer distribution → Configurer origine → Ajouter CNAME → Sélectionner certificat
3. **Route 53** : Créer enregistrement A (Alias) vers CloudFront
4. **Attendre** : 15-45 minutes
5. **Tester** : `https://mapevent.world`

---

## 💡 Astuce

**Pour le développement** :
- Utilisez `CachingDisabled` dans CloudFront pour voir les changements immédiatement
- OU invalidez le cache CloudFront après chaque modification

**Pour la production** :
- Utilisez `CachingOptimized` pour de meilleures performances
- Configurez l'invalidation automatique si vous utilisez CI/CD

---

**Créé pour Map Event - Plateforme Événementielle Mondiale 🌍**


