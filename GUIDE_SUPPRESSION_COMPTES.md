# 🗑️ GUIDE - SUPPRESSION DES COMPTES DE TEST

## 📋 Instructions rapides

### Option 1 : Supprimer TOUS les comptes SAUF votre email principal (RECOMMANDÉ)

1. **Ouvrir le script** : `supprimer_comptes_test.ps1`

2. **Modifier l'email à garder** (ligne 9) :
   ```powershell
   $emailAGarder = "VOTRE_EMAIL_PRINCIPAL@example.com"  # ⚠️ MODIFIER ICI
   ```
   Remplacez par votre vrai email principal (celui que vous voulez garder).

3. **Lancer le script** :
   ```powershell
   .\supprimer_comptes_test.ps1
   ```

4. **Confirmer** : Taper `OUI` en majuscules pour confirmer

5. **Résultat** : Tous les comptes seront supprimés SAUF votre email principal.

---

### Option 2 : Supprimer des emails spécifiques

1. **Ouvrir le script** : `delete_test_accounts.ps1`

2. **Ajouter vos emails de test** dans la liste (lignes 15-21) :
   ```powershell
   $testEmails = @(
       "test1@gmail.com",
       "test2@outlook.com",
       "test3@yahoo.com"
   )
   ```

3. **Lancer le script** :
   ```powershell
   .\delete_test_accounts.ps1
   ```

4. **Confirmer** : Taper `OUI` pour confirmer

---

## ⚠️ AVERTISSEMENTS

- ⚠️ **IRRÉVERSIBLE** : La suppression est définitive, impossible de récupérer les comptes.
- ⚠️ **Toutes les données** associées seront supprimées (likes, favoris, participations, etc.).
- ⚠️ **Avatar S3** : Les photos de profil seront supprimées de S3.

---

## 🔍 Endpoints API utilisés

### `/api/admin/delete-all-users-except` (Option 1 - RECOMMANDÉ)
- **Méthode** : POST
- **Body** : `{"keepEmail": "votre.email@example.com"}`
- **Effet** : Supprime TOUS les comptes SAUF celui spécifié
- **Avantage** : Plus sûr (garde votre compte principal)

### `/api/admin/delete-user` (Option 2)
- **Méthode** : POST
- **Body** : `{"email": "test@example.com"}`
- **Effet** : Supprime un compte spécifique
- **Avantage** : Suppression ciblée

---

## 💡 Recommandation

**Utilisez l'Option 1** (`supprimer_comptes_test.ps1`) :
- Plus simple (un seul email à spécifier)
- Plus sûr (garde votre compte principal)
- Supprime tous les comptes de test d'un coup

---

## 📝 Exemple d'utilisation

```powershell
# 1. Ouvrir supprimer_comptes_test.ps1
# 2. Modifier la ligne 9 :
$emailAGarder = "mon.email.principal@gmail.com"

# 3. Lancer le script
.\supprimer_comptes_test.ps1

# 4. Taper OUI pour confirmer
# ✅ Résultat : Tous les comptes supprimés sauf mon.email.principal@gmail.com
```

---

**Note :** Les endpoints admin n'ont pas besoin d'authentification pour faciliter les tests (à protéger en production).
