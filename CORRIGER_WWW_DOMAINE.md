# 🔧 Corriger www.mapevent.world

## 🎯 Problème

`https://www.mapevent.world` ne fonctionne pas car :
1. `www.mapevent.world` n'est pas dans les Alternate Domain Names (CNAMEs) de CloudFront
2. Il n'y a pas d'enregistrement DNS dans Route 53 pour `www`
3. Le certificat ACM doit couvrir `www.mapevent.world`

---

## 📋 Solution : 3 Étapes

### ÉTAPE 1 : Vérifier le Certificat ACM (2 min)

1. **AWS Console** → **Certificate Manager (ACM)**
2. **Certificats** → Chercher le certificat pour `mapevent.world`
3. **Vérifier les domaines** :
   - Le certificat doit contenir :
     - `mapevent.world`
     - `*.mapevent.world` (wildcard) OU `www.mapevent.world` (spécifique)

**Si `www.mapevent.world` n'est PAS dans le certificat :**

#### Option A : Ajouter www au certificat existant (si possible)
- Cliquer sur le certificat
- **Demander un nouveau certificat** OU **Demander une validation supplémentaire**
- Ajouter `www.mapevent.world` aux domaines
- Valider via DNS (créer un enregistrement CNAME dans Route 53)

#### Option B : Créer un nouveau certificat avec www
1. **Demander un certificat public**
2. **Nom de domaine** :
   - `mapevent.world`
   - `www.mapevent.world`
3. **Méthode de validation** : DNS
4. **Créer des enregistrements dans Route 53** (bouton automatique)
5. **Attendre la validation** (5-15 minutes)

---

### ÉTAPE 2 : Ajouter www dans CloudFront (3 min)

1. **AWS Console** → **CloudFront**
2. **Distributions** → Cliquer sur votre distribution
3. **Onglet "Général"** → **Modifier**
4. **Paramètres du visualiseur** → **Alternate domain names (CNAMEs)** :
   - Cliquer **Ajouter un élément**
   - Ajouter : `www.mapevent.world`
   - Vous devriez maintenant avoir :
     - `mapevent.world`
     - `www.mapevent.world`
5. **SSL certificate** :
   - **Custom SSL certificate**
   - Sélectionner le certificat qui contient `www.mapevent.world`
6. **Enregistrer les modifications**
7. ⏱️ **Attendre 5-15 minutes** pour le déploiement

---

### ÉTAPE 3 : Créer l'enregistrement DNS dans Route 53 (2 min)

1. **AWS Console** → **Route 53**
2. **Hosted zones** → Cliquer sur `mapevent.world`
3. **Créer un enregistrement**
4. **Remplir** :
   - **Nom de l'enregistrement** : `www` (pour `www.mapevent.world`)
   - **Type** : **A - Routes le trafic vers une ressource AWS**
   - **Alias** : **Oui** ✅
   - **Route le trafic vers** :
     - **Alias vers une distribution CloudFront**
     - Sélectionner votre distribution CloudFront
   - **Type d'enregistrement d'évaluation** : **A**
   - **Créer des enregistrements**

---

## ✅ Vérification

Après 15-30 minutes (propagation DNS) :

1. **Tester** : `https://www.mapevent.world`
2. **Tester** : `https://mapevent.world` (doit toujours fonctionner)

Les deux doivent fonctionner ! ✅

---

## 🐛 Dépannage

### Erreur : "Certificate not found" dans CloudFront

**Solution** :
- Vérifier que le certificat ACM est dans la région **us-east-1** (N. Virginia)
- Vérifier que `www.mapevent.world` est bien dans les domaines du certificat
- Vérifier que le certificat est **"Émis"** (pas "En attente")

### Erreur : "Access Denied" avec www

**Solution** :
- Vérifier que `www.mapevent.world` est dans les Alternate Domain Names de CloudFront
- Vérifier que le certificat sélectionné dans CloudFront contient `www.mapevent.world`
- Attendre le déploiement complet de CloudFront (statut = "Déployé")

### Le domaine www ne résout pas

**Solution** :
- Vérifier que l'enregistrement A (Alias) existe dans Route 53 pour `www`
- Vérifier que l'enregistrement pointe vers la bonne distribution CloudFront
- Attendre la propagation DNS (peut prendre jusqu'à 48h, mais généralement 15-30 min)

---

## 📋 Checklist Rapide

- [ ] Certificat ACM contient `www.mapevent.world` (ou `*.mapevent.world`)
- [ ] Certificat ACM est dans la région **us-east-1**
- [ ] Certificat ACM est **"Émis"**
- [ ] CloudFront : `www.mapevent.world` ajouté dans Alternate Domain Names
- [ ] CloudFront : Certificat sélectionné contient `www.mapevent.world`
- [ ] CloudFront : Statut = "Déployé"
- [ ] Route 53 : Enregistrement A (Alias) créé pour `www`
- [ ] Route 53 : Enregistrement pointe vers la distribution CloudFront
- [ ] Attendu 15-30 minutes
- [ ] Test : `https://www.mapevent.world` fonctionne ✅

---

## 💡 Astuce

**Pour éviter ce problème à l'avenir** :
- Lors de la création du certificat ACM, toujours inclure `www.mapevent.world`
- OU utiliser un certificat wildcard `*.mapevent.world` qui couvre automatiquement tous les sous-domaines

---

**Créé pour Map Event - Plateforme Événementielle Mondiale 🌍**







