# 🧪 Tester l'API dans Firefox - Solutions

## 🚨 Problème : Firefox bloque le collage dans la console

Firefox bloque parfois le collage (Ctrl+V) dans la console pour des raisons de sécurité.

---

## ✅ Solutions

### Solution 1 : Autoriser le collage (Firefox)

1. **Ouvrez la console** (F12)
2. **Cliquez sur l'icône ⚙️ (Paramètres)** en haut à droite de la console
3. **Cochez** "Allow pasting" ou "Autoriser le collage"
4. **Fermez les paramètres**
5. **Essayez de coller à nouveau** (Ctrl+V)

---

### Solution 2 : Tapez manuellement (si le collage ne fonctionne pas)

**Tapez ce code ligne par ligne dans la console :**

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

**Astuce :** Utilisez la touche Tab pour l'auto-complétion.

---

### Solution 3 : Créer un fichier HTML de test

**Créez un fichier `test_api.html` :**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Test API</title>
</head>
<body>
    <h1>Test API /api/user/likes</h1>
    <button onclick="testAPI()">Tester l'API</button>
    <pre id="result"></pre>
    
    <script>
        async function testAPI() {
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

**Ouvrez ce fichier dans Firefox et cliquez sur "Tester l'API".**

---

### Solution 4 : Utiliser Chrome (plus simple)

**Si Firefox pose problème, utilisez Chrome :**

1. Ouvrez Chrome
2. F12 → Console
3. Collez directement le code (Ctrl+V fonctionne dans Chrome)

---

## 💡 Méthode la Plus Simple

**Créez le fichier HTML de test (Solution 3)** - c'est le plus simple et ça fonctionne à tous les coups !



