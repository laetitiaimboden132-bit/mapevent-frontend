# Commandes Git Essentielles - Guide Rapide

## ✅ Git est maintenant installé et configuré !

Votre projet est maintenant protégé avec Git.

## 📋 Commandes essentielles

### Voir l'état des fichiers
```powershell
git status
```
Affiche les fichiers modifiés, ajoutés, supprimés.

### Sauvegarder toutes les modifications
```powershell
git add .
git commit -m "Description de ce qui a été modifié"
```

### Voir l'historique
```powershell
git log --oneline
```
Affiche tous les commits (sauvegardes).

### Voir les différences
```powershell
git diff
```
Affiche ce qui a changé depuis le dernier commit.

### Restaurer un fichier
```powershell
git checkout -- nom-du-fichier
```
Restaure un fichier à sa version du dernier commit.

### Voir une version précédente
```powershell
git log --oneline
# Copier le hash du commit souhaité
git checkout <hash-du-commit>
```

## 🚀 Workflow recommandé

### Avant de modifier le code :
```powershell
git status  # Voir ce qui a changé
```

### Après chaque modification importante :
```powershell
git add .
git commit -m "Description claire des modifications"
```

### Exemples de commits :
```powershell
git commit -m "Ajout formulaire d'inscription Google OAuth"
git commit -m "Correction affichage photo de profil"
git commit -m "Modification bouton Publier - ajout validation"
git commit -m "Réduction taille photo de profil"
```

## ⚠️ Important

**Redémarrer PowerShell** après l'installation de Git pour que les commandes fonctionnent automatiquement.

Si Git n'est pas reconnu, ajouter temporairement au PATH :
```powershell
$env:PATH += ";C:\Program Files\Git\bin"
```

## ✅ Votre projet est maintenant protégé !

Toutes vos modifications sont sauvegardées et vous pouvez restaurer n'importe quelle version précédente.








