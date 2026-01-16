# 🗑️ INSTRUCTIONS : SUPPRIMER TOUS LES COMPTES UTILISATEURS

## ⚠️ ATTENTION

Cette opération est **IRRÉVERSIBLE** ! Tous les comptes utilisateurs et leurs données seront définitivement supprimés.

---

## ✅ MÉTHODE SIMPLE (Recommandée)

### Étape 1 : Exécuter le script PowerShell

```powershell
.\supprimer-tous-comptes.ps1
```

Le script va :
1. Vous demander vos identifiants administrateur (email + mot de passe)
2. Se connecter à l'API pour obtenir un token JWT
3. Vous demander une confirmation finale (tapez "OUI")
4. Supprimer tous les comptes

### Étape 2 : Confirmer

Le script vous demandera de taper **"OUI"** en majuscules pour confirmer.

---

## 🔒 SÉCURITÉ

L'endpoint est maintenant **protégé** :
- ✅ Requiert une authentification JWT valide
- ✅ Seuls les utilisateurs avec le rôle **"director"** ou **"admin"** peuvent supprimer tous les comptes
- ✅ Requiert une confirmation explicite (`{"confirm": "yes"}`)
- ✅ Log toutes les suppressions pour audit

---

## 📋 CE QUI SERA SUPPRIMÉ

- ✅ Tous les utilisateurs
- ✅ Tous les mots de passe
- ✅ Tous les likes
- ✅ Tous les favoris
- ✅ Toutes les entrées d'agenda
- ✅ Toutes les participations
- ✅ Tous les avis
- ✅ Tous les abonnements
- ✅ Tous les avatars S3

**Note** : Les suppressions se font automatiquement via CASCADE dans PostgreSQL.

---

## 🔄 APRÈS LA SUPPRESSION

Tous les nouveaux comptes créés bénéficieront automatiquement des nouvelles mesures de sécurité :

✅ **Validation des mots de passe renforcée** (12+ caractères, complexité requise)  
✅ **Bcrypt obligatoire** (pas de fallback SHA256)  
✅ **Vérification email obligatoire**  
✅ **Photos de profil protégées** (URLs signées privées)  
✅ **Respect des paramètres de confidentialité**  
✅ **Validation des images uploadées** (type, taille, dimensions)  

---

## 🛠️ UTILISATION AVANCÉE

### Avec un token JWT existant

Si vous avez déjà un token JWT :

```powershell
.\supprimer-tous-comptes.ps1 -JwtToken "votre-token-jwt"
```

### Changer l'URL de l'API

```powershell
.\supprimer-tous-comptes.ps1 -ApiUrl "https://votre-api.com"
```

---

## ⚠️ AVANT DE SUPPRIMER

1. **Sauvegarder la base de données** (snapshot RDS recommandé)
2. **Vérifier que vous avez bien l'intention de tout supprimer**
3. **S'assurer que c'est bien l'environnement de production** (si applicable)
4. **Avoir un plan de restauration** si nécessaire

---

## 📊 EXEMPLE DE RÉSULTAT

```
============================================================
SUCCES: Tous les comptes ont ete supprimes!
============================================================

Resume:
  - Utilisateurs supprimes: 42
  - Likes supprimes: 150
  - Favoris supprimes: 89
  - Agenda supprime: 23
  - Participations supprimees: 67
  - Avis supprimes: 12
  - Mots de passe supprimes: 42
  - Abonnements supprimes: 5
  - Avatars S3 supprimes: 38
```

---

## 🎯 RÉSULTAT

Après la suppression, votre site sera prêt avec toutes les mesures de sécurité d'un site leader mondial ! 🚀



