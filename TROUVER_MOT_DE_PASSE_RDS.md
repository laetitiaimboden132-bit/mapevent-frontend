# 🔐 TROUVER LE MOT DE PASSE RDS

## 📋 Quel mot de passe utiliser ?

Vous devez utiliser le **mot de passe maître de votre base de données RDS** (pas votre mot de passe AWS).

---

## 🎯 Méthode 1 : Le mot de passe que vous avez créé lors de la création de RDS

**Lors de la création de l'instance RDS `mapevent-db`, vous avez dû entrer :**
- **Nom d'utilisateur** : `postgres` (ou un autre nom)
- **Mot de passe** : Un mot de passe que vous avez choisi

**C'est ce mot de passe qu'il faut utiliser !**

---

## 🎯 Méthode 2 : Si vous ne vous souvenez plus du mot de passe

**Vous pouvez le réinitialiser dans AWS Console :**

### Étapes :

1. **Allez sur AWS Console > RDS > Bases de données**
2. **Cliquez sur** `mapevent-db`
3. **Actions** (en haut à droite) > **Modifier**
4. **Défilez jusqu'à** "Paramètres de connexion" ou "Database authentication"
5. **Cliquez sur** "Gérer les identifiants maîtres" ou "Change master password"
6. **Entrez un nouveau mot de passe** (notez-le bien !)
7. **Confirmez le mot de passe**
8. **Sauvegardez les modifications**
9. **Cliquez sur** "Continuer" puis "Modifier la base de données"

⏱️ **ATTENTION :** La modification prendra quelques minutes (redémarrage de l'instance).

---

## 🎯 Méthode 3 : Vérifier dans vos fichiers de configuration

**Le mot de passe peut être stocké dans :**
- Variables d'environnement Lambda
- Fichiers de configuration du projet
- Variables d'environnement locales (.env)

**Cherchez dans votre projet :**
- Fichiers `.env`
- Configuration Lambda (variables d'environnement)
- Fichiers de déploiement

---

## 🎯 Méthode 4 : Utiliser Secrets Manager (si configuré)

**Si vous utilisez AWS Secrets Manager :**
1. **AWS Console > Secrets Manager**
2. **Cherchez** un secret lié à `mapevent-db`
3. **Cliquez dessus** et **Affichez la valeur du secret**

---

## 🆘 Si rien ne fonctionne

**Réinitialisez le mot de passe via AWS Console (méthode 2 ci-dessus).**

**IMPORTANT :** Après avoir réinitialisé le mot de passe, vous devrez **mettre à jour** :
- Les variables d'environnement Lambda (si utilisé)
- Tous les scripts qui utilisent ce mot de passe

---

## ✅ Après avoir trouvé/réinitialisé le mot de passe

**Notez-le dans un endroit sûr** et utilisez-le dans CloudShell :

```bash
PGPASSWORD='VOTRE_NOUVEAU_MOT_DE_PASSE' psql -h mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com -U postgres -d postgres
```

---

## 🔍 Identifier le nom d'utilisateur maître

**Sur AWS Console > RDS > mapevent-db :**
- Regardez **"Connectivité et sécurité"**
- **Identifiant principal** : C'est le nom d'utilisateur (généralement `postgres`)

