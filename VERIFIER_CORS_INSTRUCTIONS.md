# Instructions pour exécuter verifier-cors.py

## Option 1 : Naviguer vers le répertoire (RECOMMANDÉ)

```powershell
# Naviguer vers le répertoire du projet
cd C:\MapEventAI_NEW\frontend

# Exécuter le script
python verifier-cors.py
```

## Option 2 : Utiliser le chemin complet

```powershell
# Depuis n'importe quel répertoire
python C:\MapEventAI_NEW\frontend\verifier-cors.py
```

## Option 3 : Créer un alias PowerShell

Ajoutez cette fonction à votre profil PowerShell (`$PROFILE`) :

```powershell
function Verifier-CORS {
    python C:\MapEventAI_NEW\frontend\verifier-cors.py
}
```

Ensuite, vous pourrez simplement taper :
```powershell
Verifier-CORS
```

## Vérifier que vous êtes au bon endroit

```powershell
# Vérifier le répertoire actuel
pwd

# Lister les fichiers pour voir si verifier-cors.py est là
ls verifier-cors.py
```
