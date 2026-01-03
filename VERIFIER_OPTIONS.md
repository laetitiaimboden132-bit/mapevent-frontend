# 🔍 Vérifier et Configurer OPTIONS

## Le problème
OPTIONS retourne 403, ce qui signifie qu'il n'est pas correctement configuré.

## ✅ Solution : Configurer OPTIONS manuellement

### ÉTAPE 1 : Vérifier OPTIONS

1. **API Gateway** > Votre API > **Ressources**
2. `/api/payments/create-checkout-session`
3. Cliquez sur **OPTIONS** (pas POST)

### ÉTAPE 2 : Vérifier l'intégration Lambda

Sur la page OPTIONS, regardez la section **"Intégration"** ou **"Integration Request"** :

**Si vous voyez :**
- "Intégration simulée" ou "Mock Integration" → ❌ C'est le problème !

**Si vous voyez :**
- "Lambda Function" avec le nom de votre fonction → ✅ C'est bon

### ÉTAPE 3 : Configurer OPTIONS pour Lambda (si nécessaire)

Si OPTIONS n'est PAS configuré pour Lambda :

1. Cliquez sur **OPTIONS**
2. Cliquez sur **"Intégration Request"** ou **"Integration Request"**
3. Cliquez sur **"Modifier"** ou **"Edit"**
4. **Type d'intégration** : Sélectionnez **"Lambda Function"**
5. **Utiliser l'intégration proxy Lambda** : ✅ **COCHEZ**
6. **Région Lambda** : Sélectionnez votre région
7. **Fonction Lambda** : Sélectionnez votre fonction Lambda
8. Cliquez **"Enregistrer"** ou **"Save"**
9. Cliquez **"OK"** pour autoriser l'accès

### ÉTAPE 4 : Vérifier la réponse de méthode OPTIONS

1. Toujours sur OPTIONS
2. Cliquez sur **"Réponse de méthode"** ou **"Method Response"**
3. Vérifiez les **Headers de réponse** :
   - `Access-Control-Allow-Origin` doit être présent
   - `Access-Control-Allow-Methods` doit être présent
   - `Access-Control-Allow-Headers` doit être présent

**Si ces headers ne sont pas là :**
- CORS n'a pas été correctement activé sur OPTIONS
- Revenez sur POST, activez CORS à nouveau, et assurez-vous que OPTIONS est inclus

### ÉTAPE 5 : DÉPLOYER à nouveau

1. **Actions** (en haut) > **"Déployer l'API"**
2. **Stage** : `default`
3. **Description** : "Configuration OPTIONS Lambda"
4. **Déployer**
5. Attendez 30 secondes

---

## 🔍 Diagnostic rapide

Dites-moi ce que vous voyez quand vous cliquez sur **OPTIONS** :

1. **Type d'intégration** : Mock ou Lambda Function ?
2. **Lambda Proxy integration** : Coché ou non ?
3. **Réponse de méthode** : Y a-t-il les headers CORS ?

Cela m'aidera à identifier le problème exact.

