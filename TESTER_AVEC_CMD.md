# 🔧 Tester avec CMD (au lieu de PowerShell)

## ❌ Problème
Vous êtes dans **CMD** (invite de commandes) et non PowerShell.
`Invoke-WebRequest` est une commande PowerShell.

## ✅ Solution : Utiliser PowerShell

### Option 1 : Ouvrir PowerShell

1. Appuyez sur **Windows + X**
2. Sélectionnez **"Windows PowerShell"** ou **"Terminal"**
3. Ou cherchez "PowerShell" dans le menu Démarrer

### Option 2 : Utiliser curl (si installé)

Si vous avez **curl** installé, vous pouvez utiliser :

```cmd
curl -X POST https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/admin/create-tables -H "Content-Type: application/json" -d "{}"
```

### Option 3 : Utiliser PowerShell depuis CMD

Dans votre CMD actuel, tapez :

```cmd
powershell
```

Puis dans PowerShell, tapez :

```powershell
Invoke-WebRequest -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/admin/create-tables" -Method POST -Headers @{"Content-Type"="application/json"} -Body "{}"
```

## 🎯 Action immédiate

**Ouvrez PowerShell** et exécutez la commande, ou tapez `powershell` dans votre CMD actuel.

