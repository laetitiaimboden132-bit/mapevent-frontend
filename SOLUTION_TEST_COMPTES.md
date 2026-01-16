# 🧪 SOLUTIONS POUR TESTER SANS NOUVEAUX EMAILS

## ❌ POURQUOI LES ALIAS GMAIL NE FONCTIONNENT PAS

Le backend **normalise les emails Gmail** (fonction `normalize_email()` dans `main.py`) :
- Retire les points : `user.name@gmail.com` → `username@gmail.com`
- Retire les +tag : `user+1@gmail.com` → `user@gmail.com`
- Donc `user+1@gmail.com`, `user+2@gmail.com`, `user.test@gmail.com` = **même compte** ❌

---

## ✅ SOLUTIONS DISPONIBLES

### Solution 1 : Emails temporaires (RECOMMANDÉ)

Utilisez des services d'emails temporaires :

1. **10minutemail.com** (gratuit, 10 minutes)
   - Aller sur https://10minutemail.com
   - Copier l'email généré
   - Utiliser cet email pour créer le compte
   - L'email expire après 10 minutes (parfait pour les tests)

2. **tempmail.org** (gratuit, 24 heures)
   - Aller sur https://tempmail.org
   - Copier l'email généré
   - Utiliser pour créer le compte

3. **guerrillamail.com** (gratuit, 1 heure)
   - Aller sur https://guerrillamail.com
   - Copier l'email généré

**Avantage :** Pas besoin de créer de vrais comptes email, parfait pour les tests

---

### Solution 2 : Supprimer les comptes existants (si admin)

Si vous avez les droits admin, vous pouvez supprimer les comptes existants via l'API :

#### Option A : Supprimer un compte spécifique
```bash
# Via PowerShell ou curl
$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
$TOKEN = "votre_token_admin"

Invoke-WebRequest -Uri "$API_BASE/admin/delete-user" `
  -Method POST `
  -Headers @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
  } `
  -Body (@{ user_id = "ID_DU_COMPTE" } | ConvertTo-Json)
```

#### Option B : Supprimer tous les comptes SAUF un
```bash
# Garder seulement votre email principal
Invoke-WebRequest -Uri "$API_BASE/admin/delete-all-users-except" `
  -Method POST `
  -Headers @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
  } `
  -Body (@{ keep_email = "votre.email.principal@example.com" } | ConvertTo-Json)
```

⚠️ **ATTENTION :** Ces endpoints nécessitent les droits **admin** (role='admin' dans la base de données)

---

### Solution 3 : Utiliser des emails avec domaines différents

Si vous avez plusieurs domaines email :
- `test1@outlook.com`
- `test2@yahoo.com`
- `test3@hotmail.com`
- `test4@protonmail.com`

Le backend **ne normalise PAS** les emails non-Gmail, donc chaque email est unique.

---

### Solution 4 : Utiliser un compte Gmail avec plusieurs adresses

Si vous avez un compte Gmail, vous pouvez utiliser :
- `votrenom@gmail.com`
- `votrenom@googlemail.com` (alias Gmail)
- Les points ne comptent pas : `v.o.t.r.e.n.o.m@gmail.com` = `votrenom@gmail.com`

**Mais attention :** Le backend normalise `googlemail.com` → `gmail.com`, donc ces deux emails = même compte.

---

## 🎯 RECOMMANDATION

**Pour les tests rapides :** Utilisez **10minutemail.com** (Solution 1)
- Gratuit
- Pas besoin de créer de vrais comptes
- Email expire automatiquement après 10 minutes
- Parfait pour les tests

**Pour les tests réguliers :** Créez quelques comptes email gratuits avec domaines différents (Solution 3)
- Outlook.com (gratuit)
- Yahoo.com (gratuit)
- Protonmail.com (gratuit)

---

## 📋 CHECKLIST RAPIDE

1. ✅ Aller sur https://10minutemail.com
2. ✅ Copier l'email généré (ex: `abc123@10minutemail.com`)
3. ✅ Utiliser cet email pour créer le compte sur MapEvent
4. ✅ Vérifier l'email de confirmation (si nécessaire) sur 10minutemail
5. ✅ Tester votre fonctionnalité
6. ✅ L'email expire après 10 minutes automatiquement

---

**Note :** Les emails temporaires sont parfaits pour les tests car ils n'encombrent pas votre boîte mail et expirent automatiquement.
