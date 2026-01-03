# 📝 Créer les Enregistrements DNS Manuellement dans Route 53

## 🎯 Objectif

Créer les enregistrements CNAME dans Route 53 pour valider le certificat ACM.

---

## 📋 Étape 1 : Copier les Enregistrements depuis ACM

### 1.1 Aller dans ACM
- AWS Console → **Certificate Manager** (ACM)
- **Région : us-east-1** (N. Virginia)
- Cliquer sur votre certificat

### 1.2 Voir les Enregistrements DNS
- Cliquer sur le domaine **`mapevent.world`**
- Vous verrez les détails de validation
- Chercher la section **"Enregistrements DNS"** ou **"Validation DNS"**

### 1.3 Copier les Valeurs
Vous verrez quelque chose comme :

**Pour mapevent.world :**
```
Nom : _abc123def456789.mapevent.world
Type : CNAME
Valeur : _xyz789abcdef.acm-validations.aws.
```

**Pour *.mapevent.world :**
```
Nom : _abc456def789012.mapevent.world
Type : CNAME
Valeur : _xyz123abcdef.acm-validations.aws.
```

**📋 Notez ces valeurs !**

---

## 📋 Étape 2 : Aller dans Route 53

### 2.1 Ouvrir Route 53
- AWS Console → **Route 53**
- **Hosted zones** (Zones hébergées)

### 2.2 Sélectionner la Zone
- Cliquer sur **`mapevent.world`**

---

## 📋 Étape 3 : Créer le Premier Enregistrement (mapevent.world)

### 3.1 Cliquer sur "Créer un enregistrement"
- Bouton **"Créer un enregistrement"** (Create record)

### 3.2 Remplir le Formulaire

**Nom de l'enregistrement :**
- Copier depuis ACM : `_abc123def456789`
- **IMPORTANT :** Ne PAS mettre `.mapevent.world` à la fin
- Route 53 l'ajoute automatiquement
- Juste : `_abc123def456789`

**Type d'enregistrement :**
- Sélectionner **CNAME - Routes le trafic vers un autre nom de domaine**

**Valeur :**
- Copier depuis ACM : `_xyz789abcdef.acm-validations.aws.`
- **IMPORTANT :** Mettre le point (`.`) à la fin
- Juste : `_xyz789abcdef.acm-validations.aws.`

**TTL :**
- Laisser par défaut (300) ou mettre `300`

### 3.3 Créer
- Cliquer sur **"Créer des enregistrements"** (Create records)

---

## 📋 Étape 4 : Créer le Deuxième Enregistrement (*.mapevent.world)

### 4.1 Répéter les Étapes
- Cliquer sur **"Créer un enregistrement"** à nouveau

### 4.2 Utiliser les Valeurs du Wildcard
- **Nom** : `_abc456def789012` (depuis ACM pour *.mapevent.world)
- **Type** : CNAME
- **Valeur** : `_xyz123abcdef.acm-validations.aws.` (depuis ACM pour *.mapevent.world)
- **Créer**

---

## ✅ Étape 5 : Vérifier les Enregistrements

### 5.1 Dans Route 53
Vous devez voir dans la liste :
```
_abc123def456789.mapevent.world  CNAME  _xyz789abcdef.acm-validations.aws.
_abc456def789012.mapevent.world  CNAME  _xyz123abcdef.acm-validations.aws.
```

### 5.2 Vérifier les Détails
- Les noms doivent correspondre EXACTEMENT à ceux d'ACM
- Les valeurs doivent correspondre EXACTEMENT (avec le point à la fin)
- Les types doivent être CNAME

---

## ⏱️ Étape 6 : Attendre la Validation

### 6.1 Temps d'Attente
- **Normal** : 5-30 minutes
- **Maximum** : Jusqu'à 1 heure

### 6.2 Vérifier le Statut
1. Retourner dans **ACM**
2. Cliquer sur votre certificat
3. **Actualiser la page** (F5)
4. Le statut devrait passer de **"En attente de validation"** à **"Émis"**

---

## 🐛 Dépannage

### Problème : Les Enregistrements Ne Sont Pas Visibles dans ACM

**Solution :**
1. Dans ACM, cliquer sur votre certificat
2. Cliquer sur **"Statut de validation"** ou **"Domaines"**
3. Développer chaque domaine pour voir les détails
4. Les enregistrements DNS sont affichés quelque part dans les détails

### Problème : Route 53 Ne Trouve Pas la Zone

**Vérifier :**
1. Route 53 → Hosted zones
2. Vérifier qu'il y a une zone pour `mapevent.world`
3. Si elle n'existe pas, la créer d'abord

### Problème : Les Name Servers Ne Sont Pas Configurés

**Vérifier :**
1. Route 53 → Hosted zones → mapevent.world
2. Copier les 4 Name Servers (ex: `ns-123.awsdns-12.com`)
3. Dans votre registrar (où vous avez acheté mapevent.world)
4. Vérifier que ces Name Servers sont configurés
5. Si ce n'est pas le cas, les configurer

**Sans les Name Servers Route 53, les enregistrements DNS ne fonctionneront pas !**

---

## 📸 Exemple Visuel

**Dans ACM, vous verrez :**
```
Domaine : mapevent.world
Statut : En attente de validation
Enregistrements DNS :
  Nom : _abc123def456789.mapevent.world
  Valeur : _xyz789abcdef.acm-validations.aws.
```

**Dans Route 53, créer :**
```
Nom : _abc123def456789
Type : CNAME
Valeur : _xyz789abcdef.acm-validations.aws.
```

**Note :** Route 53 ajoute automatiquement `.mapevent.world` au nom.

---

## ✅ Checklist

- [ ] Enregistrements DNS copiés depuis ACM
- [ ] Route 53 → Hosted zones → mapevent.world ouvert
- [ ] Premier enregistrement CNAME créé (pour mapevent.world)
- [ ] Deuxième enregistrement CNAME créé (pour *.mapevent.world)
- [ ] Noms et valeurs correspondent EXACTEMENT
- [ ] Name Servers Route 53 configurés dans le registrar
- [ ] Attendu 5-30 minutes
- [ ] Statut ACM = "Émis"

---

## 🎯 Action Immédiate

**Faites ceci MAINTENANT :**

1. **ACM** → Votre certificat → Voir les enregistrements DNS
2. **Copier** le nom et la valeur pour chaque domaine
3. **Route 53** → mapevent.world → Créer un enregistrement
4. **Coller** les valeurs (sans `.mapevent.world` dans le nom)
5. **Créer** les 2 enregistrements
6. **Attendre** 5-30 minutes
7. **Vérifier** dans ACM que le statut passe à "Émis"

---

## 💡 Astuce

**Pour vérifier que les enregistrements sont corrects :**
- Utiliser https://dnschecker.org
- Chercher : `_abc123def456789.mapevent.world`
- Vérifier que ça retourne : `_xyz789abcdef.acm-validations.aws.`

Si ça retourne la bonne valeur, le DNS est correct et ACM devrait valider bientôt !



