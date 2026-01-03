# ✅ Résoudre "En attente de validation" - Guide Étape par Étape

## ⚠️ Problème

Votre certificat ACM est bloqué en **"En attente de validation"** car les enregistrements DNS n'ont pas été ajoutés dans Route 53.

---

## 🚀 Solution : Ajouter les Enregistrements DNS

### Étape 1 : Voir les Enregistrements Requis

1. **Aller dans ACM** (Certificate Manager)
   - AWS Console → **Certificate Manager**
   - **Important :** Vérifier que vous êtes dans **us-east-1** (N. Virginia)
   - Si vous êtes dans une autre région, changer la région en haut à droite

2. **Cliquer sur votre certificat**
   - ID : `33d9e586-7c47-4d6a-8e83-4bbad4252595`

3. **Voir les Domaines**
   - Vous verrez les domaines à valider :
     - `mapevent.world`
     - `*.mapevent.world`

4. **Voir les Enregistrements DNS**
   - Cliquer sur **"Créer un enregistrement dans Route 53"** (bouton vert/bleu)
   - **OU** aller dans l'onglet **"Statut de validation"** ou **"Domaines"**
   - Vous verrez les enregistrements CNAME à créer

**Exemple d'enregistrement :**
```
Nom : _abc123def456.mapevent.world
Type : CNAME
Valeur : _xyz789.acm-validations.aws.
```

---

### Étape 2 : Méthode Automatique (RECOMMANDÉ)

**Si vous voyez le bouton "Créer un enregistrement dans Route 53" :**

1. **Cliquer sur le bouton** (pour chaque domaine)
2. ACM va créer automatiquement les enregistrements dans Route 53
3. **Attendre 5-30 minutes**
4. **Actualiser la page ACM**
5. Le statut devrait passer à **"Émis"**

**C'est la méthode la plus simple !**

---

### Étape 3 : Méthode Manuelle (Si le bouton n'existe pas)

**Si le bouton automatique n'existe pas, créer manuellement :**

#### 3.1 Copier les Enregistrements depuis ACM

Dans ACM, pour chaque domaine, vous verrez :
- **Nom de l'enregistrement** : `_abc123def456.mapevent.world`
- **Valeur** : `_xyz789.acm-validations.aws.`

**Notez ces valeurs** (elles sont différentes pour chaque domaine).

#### 3.2 Aller dans Route 53

1. AWS Console → **Route 53**
2. **Hosted zones** (Zones hébergées)
3. Cliquer sur **`mapevent.world`**

#### 3.3 Créer les Enregistrements CNAME

**Pour le premier domaine (mapevent.world) :**

1. Cliquer sur **"Créer un enregistrement"** (Create record)
2. **Nom de l'enregistrement** :
   - Copier depuis ACM (ex: `_abc123def456`)
   - **IMPORTANT :** Ne pas mettre `.mapevent.world` (Route 53 l'ajoute automatiquement)
3. **Type d'enregistrement** :
   - Sélectionner **CNAME - Routes le trafic vers un autre nom de domaine**
4. **Valeur** :
   - Copier depuis ACM (ex: `_xyz789.acm-validations.aws.`)
   - **IMPORTANT :** Mettre le point à la fin (`.`)
5. **TTL** : Laisser par défaut (300) ou `300`
6. Cliquer sur **"Créer des enregistrements"** (Create records)

**Pour le deuxième domaine (*.mapevent.world) :**

1. Répéter les mêmes étapes
2. Utiliser les valeurs du wildcard depuis ACM
3. Créer l'enregistrement

#### 3.4 Vérifier les Enregistrements

Dans Route 53 → `mapevent.world`, vous devez voir :
```
_abc123def456.mapevent.world  CNAME  _xyz789.acm-validations.aws.
_abc456def789.mapevent.world  CNAME  _xyz123.acm-validations.aws.
```

---

### Étape 4 : Attendre la Validation

1. **Temps normal** : 5-30 minutes
2. **Maximum** : Jusqu'à 1 heure (rarement plus)

3. **Vérifier le statut** :
   - Retourner dans ACM
   - Actualiser la page (F5)
   - Le statut devrait passer de **"En attente de validation"** à **"Émis"**

---

## 🐛 Dépannage

### Problème 1 : Le Bouton "Créer un enregistrement" N'Existe Pas

**Causes possibles :**
- Route 53 n'est pas configuré pour ce domaine
- Les Name Servers Route 53 ne sont pas dans le registrar

**Solution :**
1. Vérifier que vous avez une Hosted Zone pour `mapevent.world` dans Route 53
2. Vérifier que les Name Servers Route 53 sont configurés dans votre registrar

### Problème 2 : Les Enregistrements Sont Créés Mais Pas Validés

**Vérifier :**
1. Dans Route 53, vérifier que les enregistrements existent
2. Vérifier que les **noms correspondent EXACTEMENT** (sensible à la casse)
3. Vérifier que les **valeurs correspondent EXACTEMENT** (avec le point à la fin)

**Tester avec un outil en ligne :**
- Aller sur https://dnschecker.org
- Chercher : `_abc123def456.mapevent.world`
- Vérifier que ça retourne : `_xyz789.acm-validations.aws.`

### Problème 3 : Le Certificat Est dans la Mauvaise Région

**Vérifier :**
- ACM → Vérifier la région en haut à droite
- **Doit être : us-east-1 (N. Virginia)** pour CloudFront
- Si c'est une autre région, il faut recréer le certificat dans us-east-1

### Problème 4 : Name Servers Non Configurés

**Vérifier :**
1. Route 53 → Hosted zones → `mapevent.world`
2. Copier les 4 Name Servers (ex: `ns-123.awsdns-12.com`)
3. Dans votre registrar (où vous avez acheté mapevent.world)
4. Mettre à jour les Name Servers avec ceux de Route 53

**Si les Name Servers ne sont pas configurés, les enregistrements DNS ne fonctionneront pas !**

---

## ✅ Checklist Complète

- [ ] Certificat créé dans **us-east-1** (N. Virginia)
- [ ] Bouton "Créer un enregistrement dans Route 53" cliqué (méthode automatique)
- [ ] OU enregistrements CNAME créés manuellement dans Route 53
- [ ] 2 enregistrements créés (un pour mapevent.world, un pour *.mapevent.world)
- [ ] Noms et valeurs correspondent EXACTEMENT à ceux d'ACM
- [ ] Name Servers Route 53 configurés dans le registrar
- [ ] Attendu au moins 5-30 minutes
- [ ] Statut du certificat = **"Émis"** (pas "En attente de validation")

---

## 🎯 Action Immédiate

**Faites ceci MAINTENANT :**

1. **Aller dans ACM** → Votre certificat
2. **Chercher le bouton "Créer un enregistrement dans Route 53"**
3. **Cliquer dessus** (pour chaque domaine)
4. **Attendre 5-30 minutes**
5. **Actualiser la page ACM**
6. **Vérifier** que le statut passe à "Émis"

---

## 💡 Astuce

**Si vous ne voyez pas le bouton automatique :**
- Vérifier que vous avez bien une Hosted Zone Route 53 pour `mapevent.world`
- Vérifier que les Name Servers Route 53 sont configurés dans le registrar
- Si ce n'est pas le cas, configurer d'abord les Name Servers

**Pour vérifier rapidement :**
- Aller sur https://dnschecker.org
- Chercher `mapevent.world`
- Vérifier que les Name Servers retournés sont ceux de Route 53

---

## 🆘 Si Rien Ne Fonctionne

### Option 1 : Supprimer et Recréer
1. Supprimer le certificat actuel
2. Demander un nouveau certificat
3. **Immédiatement** cliquer sur "Créer un enregistrement dans Route 53"
4. Attendre la validation

### Option 2 : Contacter le Support AWS
- Si après 1 heure, le certificat n'est toujours pas validé
- Contacter le support AWS pour vérifier

---

## 📋 Résumé

**Le problème :** Les enregistrements DNS de validation n'ont pas été ajoutés dans Route 53.

**La solution :** 
1. Cliquer sur "Créer un enregistrement dans Route 53" dans ACM
2. OU créer manuellement les enregistrements CNAME dans Route 53
3. Attendre 5-30 minutes
4. Le certificat sera validé automatiquement

**Vérifications importantes :**
- Certificat dans us-east-1
- Name Servers Route 53 configurés
- Enregistrements créés correctement



