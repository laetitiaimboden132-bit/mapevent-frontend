# Vérification Installation Git

## ⚠️ Git n'est pas encore reconnu

Cela peut arriver si :
1. PowerShell n'a pas été redémarré après l'installation
2. L'installation n'est pas terminée
3. Le PATH n'est pas encore mis à jour

## ✅ Solutions

### Solution 1 : Redémarrer PowerShell (LE PLUS SIMPLE)

1. **Fermer complètement** PowerShell
2. **Rouvrir** PowerShell (en tant qu'administrateur si possible)
3. **Tester** : `git --version`

### Solution 2 : Vérifier l'installation

1. Ouvrir **Explorateur de fichiers**
2. Aller dans : `C:\Program Files\Git\bin\`
3. Si le dossier existe, Git est installé mais le PATH n'est pas mis à jour

### Solution 3 : Vérifier les options d'installation

Si vous avez cliqué "Suivant" partout, vérifiez que :
- ✅ L'option "Git from the command line and also from 3rd-party software" était cochée par défaut
- ✅ L'installation s'est terminée sans erreur

## 🔍 Vérification manuelle

1. Ouvrir **Panneau de configuration** > **Programmes**
2. Chercher "Git" dans la liste des programmes installés
3. Si Git apparaît, il est installé mais PowerShell doit être redémarré

## ✅ Après redémarrage de PowerShell

Testez ces commandes :

```powershell
git --version
```

Vous devriez voir : `git version 2.xx.x`

Si ça fonctionne, configurez votre identité :

```powershell
git config --global user.name "Votre Nom"
git config --global user.email "votre@email.com"
```

## 🚀 Initialiser Git dans votre projet

Une fois Git reconnu :

```powershell
cd C:\MapEventAI_NEW\frontend
git init
git add .
git commit -m "Sauvegarde initiale"
```








