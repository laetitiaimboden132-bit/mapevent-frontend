# 👀 Où voir le résultat du test Lambda

## 📍 Après avoir cliqué sur "Test"

### 1. Le résultat s'affiche dans la même page

Après avoir cliqué sur **"Test"** (bouton orange), le résultat s'affiche **directement en dessous** du bouton Test.

### 2. Où regarder exactement

1. Vous êtes dans Lambda > Fonction `mapevent-backend`
2. Onglet **"Test"** (en haut)
3. Vous avez cliqué sur **"Test"** (bouton orange)
4. **En dessous** du bouton Test, vous verrez :

```
Execution result: succeeded (ou "réussi")
```

### 3. Cliquez sur "Details" (Détails)

1. Cliquez sur **"Details"** ou **"Détails"** pour voir le résultat complet
2. Vous verrez :

**Response (Réponse) :**
```json
{
  "statusCode": 200,
  "body": "{\"status\":\"success\",\"message\":\"Tables créées avec succès\",...}"
}
```

### 4. Ce que vous devez voir

**Si ça fonctionne :**
- **Execution result** : `succeeded` (réussi)
- **Response** : `statusCode: 200`
- **Body** : contient `"status":"success"` et `"message":"Tables créées avec succès"`

**Si ça ne fonctionne pas :**
- **Execution result** : `failed` (échoué)
- **Error** : message d'erreur

## 📸 À quoi ça ressemble

```
┌─────────────────────────────────────┐
│  [Test] [Configure test events]     │ ← Boutons en haut
├─────────────────────────────────────┤
│  Event name: create-tables          │
│  [JSON editor avec votre code]      │
│                                     │
│  [Test] ← Bouton orange             │
├─────────────────────────────────────┤
│  Execution result: succeeded        │ ← ICI le résultat
│  [Details] ← Cliquez ici            │
│                                     │
│  Response:                          │
│  {                                  │
│    "statusCode": 200,               │ ← ICI le 200
│    "body": "{\"status\":\"success\"}"│
│  }                                  │
└─────────────────────────────────────┘
```

## ✅ Action immédiate

1. **Cliquez sur "Test"** (bouton orange)
2. **Attendez 5 secondes**
3. **Regardez en dessous** du bouton Test
4. **Cliquez sur "Details"** pour voir le résultat complet
5. **Cherchez "statusCode: 200"** dans la réponse

## 🔍 Si vous ne voyez rien

1. **Attendez un peu** (5-10 secondes)
2. **Actualisez la page** (F5)
3. **Vérifiez que le test est en cours** (vous verrez "Running..." ou "En cours...")

Dites-moi ce que vous voyez après avoir cliqué sur "Test" !

