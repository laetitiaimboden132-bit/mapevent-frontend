# 🚀 GUIDE RAPIDE - Configuration JWT

## ✅ Étape 1 : JWT_SECRET (FAIT)

Le script `configure_jwt_secret.ps1` a été exécuté avec succès !

**Secret configuré :** `123ef56105a52cf1f84a551ff1bdbf195fe3025a5f8a6e13255ef146e3a002d4`

⚠️ **IMPORTANT** : Notez ce secret dans un endroit sûr !

---

## 📊 Étape 2 : Créer la table user_passwords

### Option A : Script Python (Recommandé)

```powershell
cd lambda-package

# Définir le mot de passe RDS
$env:RDS_PASSWORD = "VOTRE_MOT_DE_PASSE"

# Exécuter le script
python creer_table_user_passwords.py
```

### Option B : Via RDS Query Editor (AWS Console)

1. Aller dans **AWS Console** → **RDS**
2. Sélectionner **`mapevent-db`**
3. Cliquer sur **Query Editor**
4. Copier-coller le contenu de `create_user_passwords_table.sql`
5. Cliquer sur **Run**

### Option C : Automatique (lors du premier register)

La table sera créée automatiquement lors du premier `register` si elle n'existe pas, mais il est **recommandé** de la créer manuellement avant.

---

## 🧪 Étape 3 : Tester le système

```powershell
cd lambda-package
.\test_jwt.ps1
```

Ce script va :
1. ✅ Créer un utilisateur de test
2. ✅ Se connecter et obtenir les tokens JWT
3. ✅ Tester GET /api/user/me
4. ✅ Tester le refresh token
5. ✅ Vérifier que les tokens invalides sont rejetés

---

## 📝 Résumé

### ✅ Fait
- Backend déployé avec JWT
- JWT_SECRET configuré dans Lambda
- Frontend modifié pour utiliser `/api/auth/login`
- Scripts de test créés

### ⏳ À faire
- [ ] Créer la table `user_passwords` (Option A, B ou C ci-dessus)
- [ ] Tester avec `test_jwt.ps1`
- [ ] Vérifier que les nouveaux utilisateurs peuvent se connecter

---

## 🔍 Vérification rapide

```powershell
# Vérifier que JWT_SECRET est configuré
aws lambda get-function-configuration `
  --function-name mapevent-backend `
  --region eu-west-1 `
  --query 'Environment.Variables.JWT_SECRET' `
  --output text

# Devrait afficher: 123ef56105a52cf1f84a551ff1bdbf195fe3025a5f8a6e13255ef146e3a002d4
```

---

## 🆘 En cas de problème

1. **Erreur "Table user_passwords n'existe pas"**
   → Exécuter `creer_table_user_passwords.py` ou créer manuellement

2. **Erreur "JWT_SECRET non défini"**
   → Vérifier avec la commande ci-dessus, ou réexécuter `configure_jwt_secret.ps1`

3. **Erreur 401 sur /api/user/me**
   → Vérifier que le token est bien envoyé dans le header `Authorization: Bearer <token>`

4. **Erreur 500 sur /api/auth/login**
   → Vérifier les logs CloudWatch pour voir l'erreur exacte




