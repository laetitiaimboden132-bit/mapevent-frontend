# 🧪 Tester l'API SANS Serveur Local

## ✅ Vous n'avez PAS besoin du serveur local pour tester l'API !

L'API est sur AWS, vous pouvez la tester depuis n'importe quelle page web.

---

## 🚀 Méthode Rapide

### 1. Ouvrez n'importe quelle page web
- Google.com
- N'importe quel site
- Même la page d'accueil de Firefox

### 2. Ouvrez la console (F12)

### 3. Copiez-collez ce code :

```javascript
fetch('https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/likes', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ userId: '1', itemId: 1, itemMode: 'event', action: 'add' })
})
.then(r => r.json())
.then(data => {
  console.log('✅ Réponse:', data);
  alert('Succès ! Voir la console pour les détails');
})
.catch(error => {
  console.error('❌ Erreur:', error);
  alert('Erreur ! Voir la console pour les détails');
})
```

### 4. Appuyez sur Entrée

---

## 📊 Résultats

### ✅ Succès
Vous verrez dans la console :
```json
{
  "success": true,
  "action": "added",
  "message": "Like added successfully"
}
```

### ❌ Erreur 404
```json
{
  "message": "Missing Authentication Token"
}
```
**→ La route n'existe pas dans API Gateway**

### ❌ Erreur 500
```json
{
  "error": "..."
}
```
**→ Erreur dans le code Lambda (vérifier CloudWatch)**

### ❌ Erreur CORS
```
Access to fetch at '...' from origin '...' has been blocked by CORS policy
```
**→ CORS n'est pas configuré dans API Gateway**

---

## 💡 Pour Démarrer le Serveur Local (Optionnel)

**Si vous voulez voir votre site :**

```powershell
cd C:\MapEventAI_NEW\frontend\public
python -m http.server 8000
```

**Puis ouvrez :** `http://localhost:8000/mapevent.html`

**Mais ce n'est PAS nécessaire pour tester l'API !**



