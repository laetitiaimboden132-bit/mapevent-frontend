# 🎯 SOLUTION LA PLUS SIMPLE

## ❌ PROBLÈME

L'éditeur de requêtes AWS n'est pas visible dans votre menu RDS.

## ✅ SOLUTION : UTILISER PGADMIN

**pgAdmin est un outil gratuit et beaucoup plus simple** pour exécuter des requêtes SQL.

---

## 🚀 INSTALLATION RAPIDE (5 minutes)

### 1. Télécharger

- Allez sur : **https://www.pgadmin.org/download/**
- Téléchargez **pgAdmin 4 for Windows**
- Installez (double-cliquez sur le fichier .exe)

### 2. Se connecter

1. Ouvrez pgAdmin
2. Clic droit sur **"Servers"** > **"Create"** > **"Server..."**
3. Remplissez :
   - **Name** : `MapEvent`
   - **Host** : `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
   - **Port** : `5432`
   - **Database** : `mapevent`
   - **Username** : `postgres`
   - **Password** : `666666Laeti69!`
4. Cliquez sur **"Save"**

### 3. Exécuter une requête

1. Clic droit sur **"mapevent"** > **"Query Tool"**
2. Collez : `SELECT email, username, role FROM users;`
3. Cliquez sur **▶️** (bouton Execute) ou appuyez sur **F5**
4. Regardez les résultats en bas !

---

## 📝 COMMANDES À EXÉCUTER

### Voir tous les comptes :
```sql
SELECT email, username, role FROM users;
```

### Supprimer tous sauf le vôtre (remplacez l'email) :
```sql
DELETE FROM users WHERE email != 'VOTRE-EMAIL@example.com';
```

### Vérifier :
```sql
SELECT email, username, role FROM users;
```

---

## ✅ AVANTAGES DE PGADMIN

- ✅ **Gratuit** et facile à installer
- ✅ **Interface visuelle** claire
- ✅ **Bouton Execute** visible (▶️)
- ✅ **Résultats en tableau** facile à lire
- ✅ **Fonctionne partout** (pas besoin d'AWS)

---

**Installez pgAdmin, c'est la solution la plus simple !** 🚀



