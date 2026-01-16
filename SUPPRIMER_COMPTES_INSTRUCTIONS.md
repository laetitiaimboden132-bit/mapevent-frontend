# 🗑️ INSTRUCTIONS : SUPPRIMER TOUS LES COMPTES

## 📋 MÉTHODE SIMPLE

### Étape 1 : Ouvrir PowerShell dans le bon dossier

```powershell
cd C:\MapEventAI_NEW\frontend
```

### Étape 2 : Exécuter le script avec vos identifiants

**Option A : Avec email et mot de passe (recommandé)**

```powershell
.\supprimer-tous-comptes.ps1 -Email "votre-email-admin@example.com" -Password "votre-mot-de-passe"
```

**Option B : Avec un token JWT (si vous en avez déjà un)**

```powershell
.\supprimer-tous-comptes.ps1 -JwtToken "votre-token-jwt"
```

**Option C : Mode interactif (si disponible)**

```powershell
.\supprimer-tous-comptes.ps1
```

Le script vous demandera alors votre email et mot de passe.

### Étape 3 : Confirmer

Le script vous demandera de taper **"OUI"** en majuscules pour confirmer.

---

## ⚠️ IMPORTANT

- Votre compte doit avoir le rôle **"director"** ou **"admin"**
- L'URL de l'API par défaut est `https://api.mapevent.world`
- Si votre API est ailleurs, utilisez le paramètre `-ApiUrl`

**Exemple avec URL personnalisée :**
```powershell
.\supprimer-tous-comptes.ps1 -ApiUrl "https://votre-api.com" -Email "admin@example.com" -Password "motdepasse"
```

---

## ✅ CE QUI SERA SUPPRIMÉ

- Tous les utilisateurs
- Tous les mots de passe
- Tous les likes, favoris, agenda
- Tous les avatars S3
- Toutes les données associées

**⚠️ Cette opération est IRRÉVERSIBLE !**

---

## 🆘 EN CAS DE PROBLÈME

### Erreur : "Le nom distant n'a pas pu être résolu"

Cela signifie que l'URL de l'API n'est pas correcte. Vérifiez :
1. Que votre API est bien accessible
2. Utilisez le paramètre `-ApiUrl` avec la bonne URL

### Erreur : "Accès refusé"

Votre compte n'a pas les droits administrateur. Vérifiez que votre compte a le rôle "director" ou "admin".

### Erreur : "Mode interactif non disponible"

Utilisez les paramètres `-Email` et `-Password` :
```powershell
.\supprimer-tous-comptes.ps1 -Email "admin@example.com" -Password "motdepasse"
```

---

## 🎯 APRÈS LA SUPPRESSION

Tous les nouveaux comptes créés bénéficieront automatiquement du nouveau système professionnel ! 🚀



