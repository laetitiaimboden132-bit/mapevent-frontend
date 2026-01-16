# Options d'Installation Git - Guide Détaillé

## 📋 Options à cocher lors de l'installation

### Étape 1 : Sélection des composants (Select Components)

✅ **Cocher** :
- ✅ Git Bash Here
- ✅ Git GUI Here
- ✅ Associate .git* configuration files with the default text editor
- ✅ Associate .sh files to be run with Bash
- ✅ Use a TrueType font in all console windows

❌ **Décocher** (optionnel, pas nécessaire) :
- ❌ Windows Explorer integration (si vous ne voulez pas les menus contextuels)

### Étape 2 : Éditeur par défaut (Choosing the default editor)

**Recommandé** :
- ✅ **Use Visual Studio Code as Git's default editor** (si vous utilisez VS Code)
- OU
- ✅ **Use Notepad++ as Git's default editor** (si vous avez Notepad++)
- OU
- ✅ **Use Vim as Git's default editor** (si vous êtes à l'aise avec Vim)

**Éviter** :
- ❌ Nano (peut être confus pour débutants)

### Étape 3 : Ajuster le nom de la branche initiale (Adjusting your PATH environment)

**IMPORTANT - Choisir** :
- ✅ **Git from the command line and also from 3rd-party software** (RECOMMANDÉ)
  
  **Pourquoi ?** Cela permet d'utiliser Git depuis PowerShell ET depuis d'autres outils.

**Éviter** :
- ❌ Git from the command line only (limite l'utilisation)
- ❌ Use Git and optional Unix tools from the Command Prompt (peut causer des conflits)

### Étape 4 : HTTPS transport backend

**Recommandé** :
- ✅ **Use the OpenSSL library** (par défaut, meilleure compatibilité)

### Étape 5 : Configuration des fins de ligne (Configuring the line ending conversions)

**IMPORTANT - Choisir** :
- ✅ **Checkout Windows-style, commit Unix-style line endings** (RECOMMANDÉ)
  
  **Pourquoi ?** 
  - Compatible avec Windows
  - Évite les problèmes de fins de ligne
  - Standard pour la plupart des projets

**Éviter** :
- ❌ Checkout as-is, commit as-is (peut causer des problèmes)
- ❌ Checkout as-is, commit Unix-style (peut causer des problèmes sur Windows)

### Étape 6 : Terminal émulé (Configuring the terminal emulator)

**Recommandé** :
- ✅ **Use MinTTY** (terminal par défaut de Git Bash)
  
  **Pourquoi ?** Meilleure expérience utilisateur, couleurs, etc.

**Alternative** :
- Use Windows' default console window (si vous préférez l'invite Windows classique)

### Étape 7 : Comportement par défaut de `git pull`

**Recommandé** :
- ✅ **Default (fast-forward or merge)** (par défaut)
  
  **Pourquoi ?** Comportement standard et sûr

### Étape 8 : Credential Helper

**Recommandé** :
- ✅ **Git Credential Manager** (par défaut)
  
  **Pourquoi ?** Facilite la connexion à GitHub/GitLab

### Étape 9 : Options supplémentaires

✅ **Cocher** :
- ✅ Enable file system caching (améliore les performances)
- ✅ Enable symbolic links (utile pour certains projets)

## 🎯 Configuration RAPIDE (Recommandée)

Si vous voulez aller vite, cochez simplement :

1. ✅ **Git from the command line and also from 3rd-party software**
2. ✅ **Use Visual Studio Code as Git's default editor** (ou votre éditeur préféré)
3. ✅ **Checkout Windows-style, commit Unix-style line endings**
4. ✅ **Use MinTTY**
5. ✅ **Git Credential Manager**
6. ✅ **Enable file system caching**

**Tout le reste peut rester par défaut !**

## ⚠️ Après l'installation

N'oubliez pas de configurer votre identité :

```powershell
git config --global user.name "Votre Nom"
git config --global user.email "votre@email.com"
```

## ✅ Vérification

Après installation, tester dans PowerShell :

```powershell
git --version
git config --global --list
```

Vous devriez voir votre nom et email dans la liste.








