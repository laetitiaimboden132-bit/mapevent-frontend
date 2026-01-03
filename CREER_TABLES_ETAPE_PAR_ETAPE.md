# 🗄️ Créer les Tables - Guide Étape par Étape

## 🎯 Objectif
Créer toutes les tables en base de données en **2 minutes**

## ✅ Méthode : Lambda directement (la plus simple)

### 📋 ÉTAPE 1 : Ouvrir Lambda

1. Allez sur **AWS Console** (console.aws.amazon.com)
2. Dans la barre de recherche en haut, tapez : **"Lambda"**
3. Cliquez sur **"Lambda"**
4. Cliquez sur votre fonction : **`mapevent-backend`**

### 📋 ÉTAPE 2 : Aller dans l'onglet Test

1. En haut de la page Lambda, vous voyez plusieurs onglets :
   - Code
   - Test ← **CLIQUEZ ICI**
   - Monitoring
   - Configuration
   - etc.

2. Cliquez sur **"Test"**

### 📋 ÉTAPE 3 : Créer un événement de test

1. Si vous voyez **"Create new event"** ou **"Créer un nouvel événement"**, cliquez dessus
2. Si vous voyez déjà un formulaire, c'est bon

3. **Nom de l'événement** : `create-tables`

4. Dans le grand champ de texte (JSON), **effacez tout** et collez ceci :

```json
{
  "path": "/api/admin/create-tables",
  "httpMethod": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{}"
}
```

5. Cliquez sur **"Save"** (Sauvegarder) en bas

### 📋 ÉTAPE 4 : Exécuter le test

1. Cliquez sur le bouton **"Test"** (bouton orange en haut)
2. Attendez 5-10 secondes
3. Le résultat s'affiche

### 📋 ÉTAPE 5 : Vérifier le résultat

**Si vous voyez :**
```
Status: 200
Response:
{
  "status": "success",
  "message": "Tables créées avec succès",
  "tables": [...]
}
```

✅ **SUCCÈS ! Les tables sont créées !**

**Si vous voyez une erreur :**
- Copiez l'erreur complète
- Je vous aiderai à la corriger

## 📝 Sauvegarder l'événement pour plus tard

Après avoir sauvegardé l'événement `create-tables`, vous pourrez :
1. Lambda > Test
2. Sélectionner `create-tables` dans la liste déroulante
3. Cliquer "Test"
4. C'est fait en 10 secondes !

## ✅ C'est tout !

**Temps total : 2-5 minutes**

Vous n'aurez plus besoin de 3 jours, juste quelques minutes !

