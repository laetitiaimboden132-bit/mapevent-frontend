# 🧪 Tester et voir les nouveaux logs

## 📋 Étapes

### 1. Faire un NOUVEAU test MAINTENANT

Dans PowerShell, exécutez :
```powershell
Invoke-WebRequest -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/admin/create-tables" -Method POST -Headers @{"Content-Type"="application/json"} -Body "{}"
```

**Notez l'heure** de votre test (ex: 23:30)

### 2. Aller dans CloudWatch Logs

1. **CloudWatch** > **Logs** > **Log groups**
2. Cliquez sur `/aws/lambda/mapevent-backend` (ou nom similaire)
3. Cliquez sur le **log stream** le plus récent

### 3. Changer la plage de temps

1. En haut de la page CloudWatch, il y a un sélecteur de temps
2. Sélectionnez **"Last 5 minutes"** ou **"Last 15 minutes"**
3. Ou sélectionnez une plage personnalisée qui inclut l'heure actuelle

### 4. Actualiser

1. Cliquez sur **"Refresh"** (Actualiser) ou appuyez sur **F5**
2. Les nouveaux logs devraient apparaître

### 5. Chercher les logs de diagnostic

Cherchez les logs qui commencent par `🔍` :
- `🔍 Path reçu: ...`
- `🔍 Path traité: ...`
- `🔍 Méthode: ...`
- `🔍 Appel Flask: ...`
- `🔍 Réponse Flask: ...`

## 🔍 Si vous ne voyez toujours pas de nouveaux logs

### Vérifier que Lambda a été redéployé

1. **Lambda** > Fonction `mapevent-backend`
2. Onglet **"Code"**
3. Regardez la date de dernière modification
4. Si c'est ancien, Lambda n'a pas été redéployé

### Vérifier le RequestId

1. Dans les logs, cherchez un **nouveau RequestId** (différent de `d6bf8e16...`)
2. Si vous voyez toujours le même RequestId, c'est que vous regardez les anciens logs

## 📤 Envoyez-moi

Après avoir fait un **nouveau test** et changé la plage de temps, copiez-collez ici :
- Le **nouveau RequestId** (si différent)
- Tous les logs qui commencent par `🔍`
- Tous les logs entre START et END pour ce nouveau RequestId

