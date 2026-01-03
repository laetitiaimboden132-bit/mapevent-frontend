# 🔧 Comment Corriger les Variables d'Environnement Lambda

## ❌ Erreur Commune

Vous avez mis : `STRIPE_SECRET_KEY sk_test_...` dans un seul champ

## ✅ Solution : 2 Champs Séparés

Dans AWS Lambda, il y a **2 champs distincts** :

### Champ 1 : Key (Nom de la variable)
- Mettre : `STRIPE_SECRET_KEY`
- C'est le nom de la variable

### Champ 2 : Value (Valeur de la variable)
- Mettre : `sk_test_...` (votre clé complète)
- C'est la valeur réelle

---

## 📋 Étapes pour Corriger

### 1. Aller dans Lambda
- AWS Console → Lambda → Votre fonction `mapevent-backend`
- Configuration → **Environment variables** → **Edit**

### 2. Supprimer l'Ancienne Variable
- Trouver la variable avec `STRIPE_SECRET_KEY sk_test_...`
- Cliquer sur le bouton **Supprimer** (icône poubelle)

### 3. Ajouter Correctement

**Variable 1 :**
- Cliquer sur **Add environment variable**
- **Key** : `STRIPE_SECRET_KEY`
- **Value** : `sk_test_...` (uniquement la clé, sans le nom)
- Cliquer sur **Save**

**Variable 2 :**
- Cliquer sur **Add environment variable**
- **Key** : `STRIPE_PUBLIC_KEY`
- **Value** : `pk_test_...` (uniquement la clé, sans le nom)
- Cliquer sur **Save**

### 4. Vérifier
Vous devez voir dans la liste :
```
STRIPE_SECRET_KEY = sk_test_...
STRIPE_PUBLIC_KEY = pk_test_...
```

---

## 🎯 Exemple Visuel

**❌ FAUX :**
```
Key: STRIPE_SECRET_KEY sk_test_51ABC123...
Value: (vide)
```

**✅ CORRECT :**
```
Key: STRIPE_SECRET_KEY
Value: sk_test_51ABC123...
```

---

## 💡 Astuce

Si vous avez déjà mis les deux dans le même champ :
1. **Supprimer** cette variable
2. **Recréer** avec les 2 champs séparés
3. **Copier uniquement la clé** (sans "STRIPE_SECRET_KEY") dans le champ Value

---

## ✅ Checklist

- [ ] Variable supprimée si mal configurée
- [ ] Key = `STRIPE_SECRET_KEY` (sans la clé)
- [ ] Value = `sk_test_...` (uniquement la clé)
- [ ] Même chose pour `STRIPE_PUBLIC_KEY`
- [ ] Cliqué sur Save
- [ ] Vérifié que les 2 variables apparaissent correctement



