# 🔓 AUTORISER VOTRE IP DANS RDS - GUIDE FRANÇAIS

## 🎯 PROBLÈME

Vous ne pouvez pas vous connecter car votre IP n'est pas autorisée dans le Security Group.

---

## ✅ SOLUTION ÉTAPE PAR ÉTAPE

### 1. Trouver votre IP publique

**Allez sur :** https://www.whatismyip.com/

**Notez votre IP** (exemple : `81.13.194.194`)

---

### 2. Aller dans AWS RDS

1. **AWS Console** : https://console.aws.amazon.com
2. **Barre de recherche** : Tapez "RDS"
3. Cliquez sur **"RDS"**
4. Cliquez sur **"Bases de données"** dans le menu de gauche
5. Cliquez sur **"mapevent-db"**

---

### 3. Ouvrir le Security Group

1. Dans la page de votre base de données, cherchez **"Connectivité et sécurité"**
2. Cherchez **"Groupes de sécurité VPC"**
3. Vous verrez : **"default (sg-09293e0d6313eb92c)"**
4. **Cliquez sur "default"** (le nom du groupe de sécurité)

---

### 4. Ajouter votre IP

1. Une nouvelle fenêtre s'ouvre
2. Cliquez sur l'onglet **"Règles de trafic entrant"** (Inbound rules)
3. Cliquez sur **"Modifier les règles de trafic entrant"** (Edit inbound rules)
4. Cliquez sur **"Ajouter une règle"** (Add rule)
5. Remplissez :
   - **Type** : Sélectionnez **"PostgreSQL"** dans le menu déroulant
   - **Source** : 
     - Option 1 : Sélectionnez **"Mon IP"** (My IP) si disponible
     - Option 2 : Tapez votre IP avec `/32` (exemple : `81.13.194.194/32`)
   - **Description** : `Accès depuis mon ordinateur`
6. Cliquez sur **"Enregistrer les règles"** (Save rules)

---

### 5. Vérifier l'accessibilité publique

1. Retournez à la page de votre base de données
2. Dans **"Connectivité et sécurité"**, vérifiez **"Accessible publiquement"**
3. Si c'est **"Non"** :
   - Cliquez sur **"Modifier"** (Modify)
   - Dans **"Connectivité"**, cochez **"Accessible publiquement"**
   - Cliquez sur **"Continuer"** puis **"Modifier la base de données"**
   - Attendez que la modification soit terminée (5-10 minutes)

---

### 6. Réessayer la connexion

1. **Attendez 1-2 minutes** après avoir ajouté la règle
2. **Réessayez de vous connecter** dans pgAdmin
3. Ça devrait fonctionner !

---

## 📋 INFORMATIONS DE CONNEXION

Une fois votre IP autorisée, utilisez ces informations dans pgAdmin :

- **Host** : `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
- **Port** : `5432`
- **Database** : `mapevent`
- **Username** : `postgres`
- **Password** : `666666Laeti69!`

---

## ✅ RÉSUMÉ

1. ✅ Trouver votre IP : https://www.whatismyip.com/
2. ✅ RDS > mapevent-db > Security Groups > default
3. ✅ Ajouter règle : Type PostgreSQL, Source = votre IP/32
4. ✅ Vérifier "Accessible publiquement" = Oui
5. ✅ Attendre 1-2 minutes
6. ✅ Réessayer la connexion

---

**Suivez ces étapes et vous pourrez vous connecter !** 🚀
