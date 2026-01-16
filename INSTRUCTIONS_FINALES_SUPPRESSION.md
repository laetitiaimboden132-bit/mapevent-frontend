# 🚀 INSTRUCTIONS FINALES - SUPPRIMER TOUS LES COMPTES

## ✅ LE CODE A ÉTÉ DÉPLOYÉ

J'ai créé et déployé l'endpoint `/api/admin/delete-all-users-simple` dans Lambda.

---

## 🎯 MÉTHODE 1 : VIA L'API (RECOMMANDÉ)

**Attendez 1-2 minutes** que Lambda termine la mise à jour, puis :

```powershell
.\supprimer-comptes-api.ps1 -Confirm "OUI"
```

**Si ça ne fonctionne pas (erreur 502), attendez encore 1-2 minutes et réessayez.**

---

## 🎯 MÉTHODE 2 : VIA PYTHON (SI VOTRE IP EST AUTORISÉE)

**Si vous avez autorisé votre IP dans le Security Group RDS :**

```powershell
python supprimer-comptes.py
```

**Quand il demande quel compte garder, tapez juste Entrée (laissez vide) pour tout supprimer.**

---

## 🆘 SI RIEN NE FONCTIONNE

**Vérifiez les logs CloudWatch :**

1. AWS Console > Lambda > `mapevent-backend`
2. Onglet "Monitoring" > "View CloudWatch logs"
3. Regardez les dernières erreurs

---

## ✅ RÉSUMÉ

1. ✅ Code déployé dans Lambda
2. ⏳ Attendez 1-2 minutes
3. 🚀 Exécutez : `.\supprimer-comptes-api.ps1 -Confirm "OUI"`
4. ✅ Tous les comptes seront supprimés

---

**Attendez 1-2 minutes et réessayez !** 🚀


