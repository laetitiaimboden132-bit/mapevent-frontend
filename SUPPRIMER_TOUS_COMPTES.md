# 🗑️ SUPPRIMER TOUS LES COMPTES UTILISATEURS

## ⚠️ ATTENTION

Cette opération est **IRRÉVERSIBLE** ! Tous les comptes utilisateurs et leurs données associées seront supprimés.

---

## 📋 MÉTHODES DE SUPPRESSION

### Méthode 1 : Via l'API (Recommandé)

L'endpoint API `/api/admin/delete-all-users` a été créé pour supprimer tous les comptes.

**Requête** :
```bash
curl -X POST https://votre-api.com/api/admin/delete-all-users \
  -H "Content-Type: application/json" \
  -d '{"confirm": "yes"}'
```

**Via PowerShell** :
```powershell
$body = @{
    confirm = "yes"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://votre-api.com/api/admin/delete-all-users" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

---

### Méthode 2 : Via Script Python (Local)

Si vous avez accès direct à la base de données RDS :

```powershell
# Charger les variables d'environnement depuis lambda.env
Get-Content lambda-package/lambda.env | Where-Object { $_ -match '^[^#].*=' } | ForEach-Object { 
    $parts = $_ -split '=', 2
    if ($parts.Length -eq 2) { 
        [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), 'Process') 
    }
}

# Confirmer et exécuter
$env:CONFIRM_DELETE_ALL="yes"
python lambda-package/delete_all_users.py
```

**Note** : Cette méthode nécessite un accès réseau direct à RDS (depuis une instance EC2 dans le même VPC, par exemple).

---

## ✅ CE QUI SERA SUPPRIMÉ

- ✅ Tous les utilisateurs de la table `users`
- ✅ Tous les mots de passe de la table `user_passwords`
- ✅ Tous les likes de la table `user_likes`
- ✅ Tous les favoris de la table `user_favorites`
- ✅ Toutes les entrées d'agenda de la table `user_agenda`
- ✅ Toutes les participations de la table `user_participations`
- ✅ Tous les avis de la table `user_reviews`
- ✅ Tous les abonnements de la table `subscriptions`
- ✅ Tous les avatars S3 associés

**Note** : Les suppressions se font automatiquement via CASCADE dans PostgreSQL.

---

## 🔒 SÉCURITÉ

L'endpoint `/api/admin/delete-all-users` :
- ✅ Requiert une confirmation explicite (`{"confirm": "yes"}`)
- ✅ Log toutes les suppressions
- ✅ Retourne un résumé détaillé des données supprimées
- ⚠️ **N'est PAS protégé par authentification** - À ajouter si nécessaire

**Recommandation** : Ajouter une protection par JWT ou API key avant d'utiliser cet endpoint en production.

---

## 📊 EXEMPLE DE RÉPONSE

```json
{
  "success": true,
  "message": "Tous les comptes utilisateurs ont été supprimés avec succès",
  "deleted_count": 42,
  "deleted_data": {
    "users": 42,
    "likes": 150,
    "favorites": 89,
    "agenda": 23,
    "participations": 67,
    "reviews": 12,
    "passwords": 42,
    "subscriptions": 5,
    "avatars_s3": 38
  }
}
```

---

## ⚠️ AVANT DE SUPPRIMER

1. **Sauvegarder la base de données** (snapshot RDS recommandé)
2. **Vérifier que vous avez bien l'intention de tout supprimer**
3. **S'assurer que c'est bien l'environnement de production** (si applicable)
4. **Avoir un plan de restauration** si nécessaire

---

## 🔄 APRÈS LA SUPPRESSION

Tous les nouveaux comptes créés bénéficieront automatiquement des nouvelles mesures de sécurité :
- ✅ Validation des mots de passe renforcée (12+ caractères, complexité)
- ✅ Bcrypt obligatoire
- ✅ Vérification email obligatoire
- ✅ Photos de profil protégées (URLs signées)
- ✅ Respect des paramètres de confidentialité



