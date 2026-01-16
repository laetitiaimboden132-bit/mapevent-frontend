# ✅ SOLUTION SIMPLE : AWS RDS Query Editor

## 🎯 Utiliser AWS RDS Query Editor (PAS BESOIN DE CONNEXION LOCALE !)

### Étape 1 : Ouvrir l'éditeur de requêtes AWS

1. **Allez sur AWS Console** : https://console.aws.amazon.com
2. **RDS** > **Bases de données** > **mapevent-db**
3. **Cliquez sur** "Éditeur de requêtes" ou "Query Editor" (en haut de la page)

---

### Étape 2 : Se connecter

1. **Identifiant de connexion** : `postgres` (ou votre identifiant principal)
2. **Mot de passe** : Votre mot de passe RDS principal
3. **Base de données** : `postgres` (ou le nom de votre base)
4. **Cliquez sur** "Se connecter"

---

### Étape 3 : Copier le script SQL

1. **Ouvrez le fichier** `supprimer-comptes-sauf-admin.sql`
2. **Copiez tout le contenu**

---

### Étape 4 : Modifier l'email admin

**Dans le script, cherchez cette ligne :**
```sql
WHERE email = 'admin@example.com'
```

**Remplacez `admin@example.com` par l'email de VOTRE compte admin**

**Par exemple :**
```sql
WHERE email = 'votre.email@admin.com'
```

---

### Étape 5 : Exécuter le script

1. **Collez le script** dans l'éditeur de requêtes AWS
2. **Vérifiez** que l'email admin est correct
3. **Cliquez sur** "Exécuter" ou "Run"

---

### Étape 6 : Vérifier

**Le script affichera :**
- **Avant** : Tous les comptes existants
- **Après** : UN SEUL compte (votre admin)

---

## ✅ Avantages de cette méthode

- ✅ **Pas besoin de connexion locale** (contourne McAfee, firewall, etc.)
- ✅ **Pas besoin de modifier le Security Group**
- ✅ **Exécution directe sur AWS**
- ✅ **Interface graphique simple**
- ✅ **Voir les résultats immédiatement**

---

## 🆘 Si vous ne trouvez pas "Éditeur de requêtes"

**Alternative :**
1. **RDS** > **mapevent-db** > **Actions** > **Connecter à l'aide du terminal**
2. Ou utilisez **AWS CloudShell** (terminal web dans AWS)

---

## 📝 Script SQL

**Le script supprime :**
- ✅ Tous les favoris
- ✅ Tous les agendas
- ✅ Tous les likes
- ✅ Toutes les souscriptions
- ✅ Tous les mots de passe
- ✅ Tous les profils
- ✅ **TOUS LES COMPTES SAUF VOTRE ADMIN**

---

**C'est la méthode la plus simple !** 🚀

