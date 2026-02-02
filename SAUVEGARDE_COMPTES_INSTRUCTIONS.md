# 💾 Instructions de Sauvegarde des Comptes

## 📋 Scripts Créés

1. **`sauvegarder-comptes-complet.py`** - Sauvegarde tous les comptes utilisateurs
2. **`restaurer-comptes-complet.py`** - Restaure les comptes depuis une sauvegarde

## 🚀 Utilisation

### Sauvegarder les comptes

```bash
# Définir le mot de passe RDS
$env:RDS_PASSWORD = "votre_mot_de_passe_rds"

# Exécuter la sauvegarde
python sauvegarder-comptes-complet.py
```

**OU** modifier le script pour utiliser le mot de passe depuis `lambda-package/lambda.env`

### Restaurer les comptes

```bash
# Définir le mot de passe RDS
$env:RDS_PASSWORD = "votre_mot_de_passe_rds"

# Restaurer depuis la dernière sauvegarde
python restaurer-comptes-complet.py

# OU spécifier un fichier
python restaurer-comptes-complet.py sauvegardes/comptes_utilisateurs_20260119_120000.json
```

## 📁 Fichiers Créés

- **`sauvegardes/comptes_utilisateurs_YYYYMMDD_HHMMSS.json`** - Fichier JSON complet
- **`sauvegardes/resume_comptes_YYYYMMDD_HHMMSS.txt`** - Résumé lisible

## ✅ Ce qui est Sauvegardé

- ✅ Tous les utilisateurs (`users`)
- ✅ Tous les mots de passe (`user_passwords`)
- ✅ Tous les profils (`user_profiles`)
- ✅ Tous les tokens de vérification (`email_verification_tokens`)
- ✅ Tous les likes (`user_likes`)
- ✅ Tous les favoris (`user_favorites`)
- ✅ Toutes les participations (`user_participations`)
- ✅ Tous les agendas (`user_agenda`)
- ✅ Tous les avis (`user_reviews`)
- ✅ Toutes les amitiés (`user_friends`)
- ✅ Tous les abonnements (`subscriptions`)
- ✅ Toutes les alertes (`user_alerts`, `user_alert_settings`)
- ✅ Tous les signalements (`user_reports`)
- ✅ Tous les groupes (`groups`, `group_members`)

## 🔒 Sécurité

⚠️ **IMPORTANT**: Les fichiers de sauvegarde contiennent des mots de passe hashés et des données sensibles. 
- Ne pas partager ces fichiers
- Les stocker dans un endroit sécurisé
- Les supprimer après restauration si nécessaire
