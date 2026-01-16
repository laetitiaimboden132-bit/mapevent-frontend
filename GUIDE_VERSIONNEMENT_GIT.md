# Guide de Versionnement avec Git

## Pourquoi utiliser Git ?

Git permet de :
- ✅ Sauvegarder toutes les modifications
- ✅ Voir l'historique complet des changements
- ✅ Restaurer des versions précédentes
- ✅ Travailler en équipe sans perdre de code
- ✅ Créer des branches pour tester des fonctionnalités

## Commandes Git essentielles

### Initialiser un dépôt Git (si pas déjà fait)
```bash
cd C:\MapEventAI_NEW\frontend
git init
```

### Voir l'état des fichiers
```bash
git status
```

### Ajouter tous les fichiers modifiés
```bash
git add .
```

### Créer un commit (sauvegarde)
```bash
git commit -m "Description des modifications"
```

### Voir l'historique des commits
```bash
git log --oneline
```

### Restaurer une version précédente
```bash
git checkout <hash-du-commit>
```

## Workflow recommandé

1. **Avant de modifier** : `git status` pour voir ce qui a changé
2. **Après chaque modification importante** : 
   ```bash
   git add .
   git commit -m "Description claire des modifications"
   ```
3. **Avant de déployer** : Créer un commit de sauvegarde
4. **Après déploiement** : Créer un commit "Deployed to production"

## Exemple de commits

```bash
git commit -m "Ajout formulaire d'inscription Google OAuth"
git commit -m "Correction affichage photo de profil"
git commit -m "Modification bouton Publier - ajout validation"
git commit -m "Deployed to production - 2024-01-02"
```

## Sauvegarder sur GitHub/GitLab (optionnel mais recommandé)

```bash
# Créer un dépôt sur GitHub, puis :
git remote add origin https://github.com/votre-username/mapevent.git
git push -u origin main
```

## Avantages

- ✅ **Historique complet** : Toutes les modifications sont sauvegardées
- ✅ **Restauration facile** : Retour à n'importe quelle version
- ✅ **Traçabilité** : Savoir qui a modifié quoi et quand
- ✅ **Sécurité** : Code sauvegardé sur serveur distant








