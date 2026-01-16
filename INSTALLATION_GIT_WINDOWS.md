# Installation Git sur Windows - Guide Complet

## ✅ OUI, Git est 100% GRATUIT !

Git est un logiciel **open source** et **gratuit**. Aucun coût, aucune limitation.

## 📥 Installation

### Option 1 : Téléchargement direct (Recommandé)

1. **Aller sur** : https://git-scm.com/download/win
2. **Télécharger** : Le fichier `.exe` (environ 50 MB)
3. **Exécuter** : Le fichier téléchargé
4. **Installer** : Suivre l'assistant d'installation avec les options par défaut

### Option 2 : Via winget (si disponible)

```powershell
winget install --id Git.Git -e --source winget
```

### Option 3 : Via Chocolatey (si installé)

```powershell
choco install git
```

## ⚙️ Options d'installation recommandées

Lors de l'installation, choisissez :

- ✅ **Git from the command line and also from 3rd-party software** (recommandé)
- ✅ **Use Visual Studio Code as Git's default editor** (si vous utilisez VS Code)
- ✅ **Use bundled OpenSSH**
- ✅ **Use the OpenSSL library**
- ✅ **Checkout Windows-style, commit Unix-style line endings** (par défaut)
- ✅ **Use MinTTY** (terminal par défaut)

## ✅ Vérifier l'installation

Après installation, ouvrir PowerShell et taper :

```powershell
git --version
```

Vous devriez voir quelque chose comme : `git version 2.43.0`

## 🚀 Première configuration

Après installation, configurer votre identité :

```powershell
git config --global user.name "Votre Nom"
git config --global user.email "votre@email.com"
```

## 📚 Utilisation basique

### Initialiser Git dans votre projet

```powershell
cd C:\MapEventAI_NEW\frontend
git init
```

### Créer votre premier commit

```powershell
git add .
git commit -m "Premier commit - sauvegarde initiale"
```

### Voir l'historique

```powershell
git log --oneline
```

## 💡 Avantages de Git

- ✅ **100% gratuit** et open source
- ✅ **Sauvegarde automatique** de toutes les modifications
- ✅ **Historique complet** de tous les changements
- ✅ **Restauration facile** de n'importe quelle version
- ✅ **Travail en équipe** facilité
- ✅ **Branches** pour tester sans risque

## 🔗 Ressources

- **Site officiel** : https://git-scm.com/
- **Documentation** : https://git-scm.com/doc
- **Tutoriel interactif** : https://learngitbranching.js.org/

## ⚠️ Important

Une fois Git installé, vous pourrez :
1. Sauvegarder toutes vos modifications
2. Voir exactement ce qui a changé
3. Restaurer n'importe quelle version précédente
4. Travailler sans risque de perdre du code

**C'est le meilleur moyen de protéger votre code !**








