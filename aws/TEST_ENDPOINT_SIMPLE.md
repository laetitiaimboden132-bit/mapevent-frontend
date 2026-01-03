# 🧪 Test Simple de l'Endpoint /api/user/likes

## 📋 Méthode Rapide

### Option 1 : Console du Navigateur (Recommandé)

1. **Ouvrez votre navigateur**
2. **Ouvrez la console** (F12)
3. **Copiez-collez ce code** :

```javascript
fetch('https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/likes', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ userId: '1', itemId: 1, itemMode: 'event', action: 'add' })
})
.then(r => r.json())
.then(data => console.log('✅ Réponse:', data))
.catch(error => console.error('❌ Erreur:', error))
```

4. **Appuyez sur Entrée**

---

### Option 2 : Page de Test HTML

**Créez un fichier `test_endpoint.html` :**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Test Endpoint</title>
</head>
<body>
    <h1>Test Endpoint /api/user/likes</h1>
    <button onclick="testEndpoint()">Tester</button>
    <pre id="result"></pre>
    
    <script>
        async function testEndpoint() {
            const resultEl = document.getElementById('result');
            resultEl.textContent = 'Envoi de la requête...';
            
            try {
                const response = await fetch('https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/likes', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        userId: '1', 
                        itemId: 1, 
                        itemMode: 'event', 
                        action: 'add' 
                    })
                });
                
                const data = await response.json();
                resultEl.textContent = JSON.stringify(data, null, 2);
                
                if (data.success) {
                    resultEl.style.color = 'green';
                } else {
                    resultEl.style.color = 'red';
                }
            } catch (error) {
                resultEl.textContent = 'Erreur: ' + error.message;
                resultEl.style.color = 'red';
            }
        }
    </script>
</body>
</html>
```

**Ouvrez ce fichier dans votre navigateur et cliquez sur "Tester".**

---

## 📊 Résultats Possibles

### ✅ Succès (200 OK)
```json
{
  "success": true,
  "action": "added",
  "message": "Like added successfully"
}
```

### ❌ Erreur 404 - Route non trouvée
```json
{
  "message": "Missing Authentication Token"
}
```
**→ La route n'existe pas dans API Gateway ou l'API n'est pas déployée**

### ❌ Erreur 500 - Erreur serveur
```json
{
  "error": "..."
}
```
**→ Vérifiez les logs CloudWatch**

### ❌ Erreur Foreign Key
```json
{
  "error": "insert or update on table \"user_likes\" violates foreign key constraint"
}
```
**→ L'utilisateur avec l'ID "1" n'existe pas dans la base de données**

---

## 💡 Note sur l'Erreur Redux

**L'erreur Redux que vous voyez :**
```
Unexpected key "TrendingSearch" found in previous state...
```

**C'est une erreur interne de Firefox** (onglet nouveau), **PAS de notre application**. Vous pouvez l'ignorer.

**Pour éviter cette erreur :**
- Testez sur une page de votre site (mapevent.html)
- Ou utilisez Chrome pour tester
- Ou ignorez simplement cette erreur (elle n'affecte pas notre test)



