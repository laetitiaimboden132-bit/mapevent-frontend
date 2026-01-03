# 🔒 Valider le Certificat ACM - Guide de Dépannage

## ⚠️ Problème : Certificat "En attente de validation"

Votre certificat ACM est bloqué en **"En attente de validation"** depuis plusieurs heures.

**Cause :** Les enregistrements DNS de validation n'ont pas été ajoutés dans Route 53.

---

## 🔍 Étape 1 : Vérifier les Enregistrements DNS Requis

### 1.1 Aller dans ACM
- AWS Console → **Certificate Manager** (ACM)
- **Important :** Vérifier que vous êtes dans la région **us-east-1** (N. Virginia)
- Trouver votre certificat (ID: `33d9e586-7c47-4d6a-8e83-4bbad4252595`)

### 1.2 Voir les Enregistrements DNS
- Cliquer sur votre certificat
- Aller dans l'onglet **"Domaines"**
- Vous verrez les domaines à valider :
  - `mapevent.world`
  - `*.mapevent.world` (wildcard)

### 1.3 Voir les Enregistrements de Validation
- Cliquer sur **"Créer un enregistrement dans Route 53"** (si disponible)
- OU aller dans l'onglet **"Statut de validation"**
- Vous verrez les enregistrements CNAME à ajouter

**Exemple d'enregistrement :**
```
Nom : _abc123def456.mapevent.world
Type : CNAME
Valeur : _xyz789.acm-validations.aws.
```

---

## 📝 Étape 2 : Ajouter les Enregistrements dans Route 53

### 2.1 Aller dans Route 53
- AWS Console → **Route 53**
- **Hosted zones** → Cliquer sur `mapevent.world`

### 2.2 Créer les Enregistrements CNAME

Pour chaque domaine à valider, créer un enregistrement CNAME :

**Enregistrement 1 : Pour mapevent.world**
- Cliquer sur **"Créer un enregistrement"**
- **Nom de l'enregistrement** : Copier depuis ACM (ex: `_abc123def456`)
- **Type** : `CNAME - Routes le trafic vers un autre nom de domaine`
- **Valeur** : Copier depuis ACM (ex: `_xyz789.acm-validations.aws.`)
- **TTL** : `300` (ou laisser par défaut)
- Cliquer sur **"Créer des enregistrements"**

**Enregistrement 2 : Pour *.mapevent.world (wildcard)**
- Même processus avec les valeurs pour le wildcard

### 2.3 Vérifier les Enregistrements
Vous devez voir dans Route 53 :
```
_abc123def456.mapevent.world  CNAME  _xyz789.acm-validations.aws.
_abc456def789.mapevent.world  CNAME  _xyz123.acm-validations.aws.
```

---

## ⏱️ Étape 3 : Attendre la Validation

### 3.1 Temps de Propagation DNS
- **Normalement** : 5-30 minutes
- **Maximum** : Jusqu'à 48 heures (rare)
- **Si > 1 heure** : Vérifier que les enregistrements sont corrects

### 3.2 Vérifier le Statut
- Retourner dans ACM
- Actualiser la page
- Le statut devrait passer de **"En attente de validation"** à **"Émis"**

---

## 🐛 Dépannage : Si Ça Ne Fonctionne Pas

### Problème 1 : Les Enregistrements Ne Sont Pas Visibles

**Solution :**
1. Dans ACM, cliquer sur votre certificat
2. Cliquer sur **"Créer un enregistrement dans Route 53"** (bouton)
3. ACM va créer automatiquement les enregistrements

### Problème 2 : Les Enregistrements Sont Créés Mais Pas Validés

**Vérifier :**
1. Dans Route 53, vérifier que les enregistrements existent
2. Vérifier que les noms correspondent EXACTEMENT (sensible à la casse)
3. Vérifier que les valeurs correspondent EXACTEMENT

**Tester avec dig (si disponible) :**
```bash
dig _abc123def456.mapevent.world CNAME
```
Doit retourner la valeur `_xyz789.acm-validations.aws.`

### Problème 3 : Le Certificat Est dans la Mauvaise Région

**Vérifier :**
- ACM → Vérifier que vous êtes dans **us-east-1** (N. Virginia)
- CloudFront nécessite les certificats dans us-east-1
- Si le certificat est dans une autre région, il faut le recréer dans us-east-1

### Problème 4 : Route 53 N'est Pas le DNS Principal

**Vérifier :**
- Dans votre registrar (où vous avez acheté mapevent.world)
- Vérifier que les Name Servers (NS) de Route 53 sont configurés
- Si ce n'est pas le cas, les enregistrements DNS ne fonctionneront pas

**Vérifier les Name Servers :**
1. Route 53 → Hosted zones → mapevent.world
2. Copier les 4 Name Servers (ex: `ns-123.awsdns-12.com`)
3. Dans votre registrar, mettre à jour les Name Servers

---

## 🔄 Solution Rapide : Utiliser le Bouton Automatique

### Méthode la Plus Simple

1. **Dans ACM** :
   - Cliquer sur votre certificat
   - Cliquer sur **"Créer un enregistrement dans Route 53"** (bouton vert)
   - ACM va créer automatiquement les enregistrements

2. **Attendre 5-30 minutes**

3. **Vérifier** :
   - Actualiser la page ACM
   - Le statut devrait passer à **"Émis"**

---

## ✅ Checklist de Validation

- [ ] Certificat créé dans **us-east-1** (N. Virginia)
- [ ] Enregistrements DNS visibles dans ACM
- [ ] Enregistrements créés dans Route 53 (manuellement ou automatiquement)
- [ ] Name Servers Route 53 configurés dans le registrar
- [ ] Attendu au moins 5-30 minutes
- [ ] Statut du certificat = **"Émis"** (pas "En attente de validation")

---

## 🆘 Si Rien Ne Fonctionne

### Option 1 : Supprimer et Recréer
1. Supprimer le certificat actuel
2. Demander un nouveau certificat
3. Utiliser le bouton **"Créer un enregistrement dans Route 53"** immédiatement

### Option 2 : Validation par Email
Si la validation DNS ne fonctionne pas :
1. Dans ACM, cliquer sur votre certificat
2. Choisir **"Validation par email"** (au lieu de DNS)
3. Vérifier l'email et cliquer sur le lien

**Note :** La validation par email fonctionne seulement pour `mapevent.world`, pas pour `*.mapevent.world`

---

## 📋 Résumé : Actions Immédiates

1. **Aller dans ACM** → Votre certificat
2. **Cliquer sur "Créer un enregistrement dans Route 53"** (si disponible)
3. **OU** copier les enregistrements CNAME et les créer manuellement dans Route 53
4. **Attendre 5-30 minutes**
5. **Vérifier** que le statut passe à "Émis"

---

## 💡 Astuce

**Le bouton automatique est le plus simple :**
- ACM peut créer les enregistrements automatiquement
- Plus rapide et moins d'erreurs
- Utilisez-le si disponible !

---

## 🔗 Vérification

**Pour vérifier que les enregistrements DNS sont corrects :**
- Utiliser un outil en ligne : https://dnschecker.org
- Chercher : `_abc123def456.mapevent.world`
- Vérifier que ça retourne : `_xyz789.acm-validations.aws.`

Si ça retourne la bonne valeur, le DNS est correct et ACM devrait valider bientôt.



