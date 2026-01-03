# 🚀 Guide de Démarrage - MapEventAI

## ⚠️ Problème de Connexion Firefox

Si vous voyez "Impossible de se connecter au serveur à l'adresse localhost", cela peut être dû à :

### 1. Proxy Firefox
Firefox peut avoir un proxy configuré qui bloque localhost.

**Solution** :
1. Ouvrez Firefox
2. Menu (☰) > **Paramètres** (ou `about:preferences`)
3. Faites défiler jusqu'à **Réseau**
4. Cliquez sur **Paramètres...**
5. Sélectionnez **Aucun proxy**
6. Cliquez **OK**
7. Réessayez : `http://127.0.0.1:8000/mapevent.html`

### 2. Utilisez 127.0.0.1 au lieu de localhost

Essayez ces URLs :
- ✅ `http://127.0.0.1:8000/mapevent.html` (recommandé)
- ✅ `http://localhost:8000/mapevent.html`

## 📋 Démarrage des Serveurs

### Option 1 : Script Automatique
```bash
start_servers.bat
```

### Option 2 : Manuel (2 terminaux)

**Terminal 1 - Backend** :
```bash
cd c:\MapEventAI_NEW\backend
python main.py
```

**Terminal 2 - Frontend** :
```bash
cd c:\MapEventAI_NEW\frontend\public
python -m http.server 8000
```

### Option 3 : Test et Diagnostic
```bash
test_servers.bat
```

## 🔗 URLs du Site

- **Frontend** : `http://127.0.0.1:8000/mapevent.html`
- **Backend API** : `http://127.0.0.1:5005`
- **Health Check** : `http://127.0.0.1:5005/health`

## 🛠️ Vérification

Vérifiez que les serveurs sont actifs :
```bash
netstat -ano | findstr ":8000 :5005"
```

Vous devriez voir les ports en état LISTENING.

## ❌ Problèmes Courants

### "Python n'est pas reconnu"
- Installez Python depuis python.org
- Ajoutez Python au PATH lors de l'installation

### "Flask n'est pas installé"
```bash
pip install flask flask-cors
```

### "Port déjà utilisé"
- Fermez les autres applications utilisant les ports 8000 ou 5005
- Ou changez les ports dans les scripts

### "Firefox bloque localhost"
- Désactivez le proxy (voir section 1 ci-dessus)
- Utilisez `127.0.0.1` au lieu de `localhost`
- Essayez avec Chrome ou Edge

































