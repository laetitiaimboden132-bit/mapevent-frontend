# 📋 CHECKLIST - À FAIRE CE SOIR (10 minutes)

## ✅ CE QUI EST DÉJÀ FAIT (automatiquement)

- ✅ **Secrets Manager** : 4 secrets créés et intégrés dans le code
- ✅ **CloudWatch Alarms** : 3 alarmes créées pour détecter les attaques
- ✅ **Security Headers Policy** : Créée et prête à être associée
- ✅ **Code Lambda** : Modifié pour utiliser Secrets Manager
- ✅ **RDS** : Déjà chiffré (KMS)

---

## ⚠️ CE QU'IL RESTE À FAIRE (10 minutes)

### ÉTAPE 1 : S'abonner aux alertes SNS (5 minutes)

**Où** : AWS Console > SNS > Topics > `mapevent-security-alerts`

**Actions** :
1. AWS Console > Chercher "SNS"
2. Topics > `mapevent-security-alerts`
3. Create subscription > Email
4. Entrer votre email
5. Confirmer l'abonnement (email reçu)

**Guide détaillé** : `GUIDE_ACTIONS_MANUELLES_SECURITE.md` (section ÉTAPE 1)

---

### ÉTAPE 2 : Associer Security Headers à CloudFront (5 minutes)

**Où** : AWS Console > CloudFront > Distributions > `EMB53HDL7VFIJ`

**Actions** :
1. CloudFront > Distribution `EMB53HDL7VFIJ`
2. Onglet "Behaviors"
3. Éditer le premier behavior (`*`)
4. Response Headers Policy : `mapevent-security-headers-policy`
5. Save changes

**Guide détaillé** : `GUIDE_ACTIONS_MANUELLES_SECURITE.md` (section ÉTAPE 2)

---

## ✅ VÉRIFICATION FINALE

Après avoir fait les 2 étapes, lancer :

```bash
python verifier-configuration-securite.py
```

**Résultat attendu** : "OK: TOUT EST CONFIGURE CORRECTEMENT !"

---

## 📁 FICHIERS UTILES

- **`GUIDE_ACTIONS_MANUELLES_SECURITE.md`** : Guide détaillé pas à pas
- **`verifier-configuration-securite.py`** : Script de vérification
- **`RESUME_SECURITE_LEADER_MONDIAL.md`** : Résumé complet

---

## 🎯 RÉSULTAT FINAL

Une fois les 2 étapes terminées, votre système sera **au niveau de sécurité d'un leader mondial** ! 🛡️

**Temps total** : 10 minutes
**Difficulté** : Facile (juste cliquer dans AWS Console)

---

**Bonne soirée ! À ce soir pour finaliser ! 🚀**
