# 🔧 CORRIGER L'ERREUR DE TIMEOUT

## ❌ PROBLÈME

**"Unable to connect to server: connection timeout expired"**

Cela signifie que votre **IP n'est pas autorisée** dans le Security Group de votre base de données RDS.

---

## ✅ SOLUTION : AUTORISER VOTRE IP

### Étape 1 : Trouver votre IP publique

1. Allez sur : **https://www.whatismyip.com/**
2. **Notez votre IP publique** (exemple : `81.13.194.194`)

---

### Étape 2 : Autoriser votre IP dans AWS

1. **Dans AWS Console**, allez dans **RDS**
2. Cliquez sur votre base de données **"mapevent-db"**
3. Dans la section **"Connectivité et sécurité"**, cherchez **"Groupes de sécurité VPC"**
4. Vous verrez : **"default (sg-09293e0d6313eb92c)"** - **Cliquez dessus**
5. Une nouvelle fenêtre s'ouvre avec les règles de sécurité

### Étape 3 : Ajouter une règle pour votre IP

1. Cliquez sur l'onglet **"Règles de trafic entrant"** (Inbound rules)
2. Cliquez sur **"Modifier les règles de trafic entrant"** (Edit inbound rules)
3. Cliquez sur **"Ajouter une règle"** (Add rule)
4. Remplissez :
   - **Type** : `PostgreSQL` (ou sélectionnez dans la liste)
   - **Source** : `Mon IP` OU tapez votre IP avec `/32` (exemple : `81.13.194.194/32`)
   - **Description** : `Accès depuis mon ordinateur`
5. Cliquez sur **"Enregistrer les règles"** (Save rules)

---

### Étape 4 : Réessayer la connexion

1. **Attendez 1-2 minutes** (le temps que la règle soit appliquée)
2. **Réessayez de vous connecter** dans pgAdmin
3. Ça devrait fonctionner maintenant !

---

## 🆘 SI ÇA NE FONCTIONNE TOUJOURS PAS

### Vérifier que la base est accessible publiquement

Dans les détails de votre base de données RDS :
- **"Accessible publiquement"** doit être **"Oui"**

Si c'est "Non" :
1. Cliquez sur **"Modifier"** (Modify)
2. Dans **"Connectivité"**, cochez **"Accessible publiquement"**
3. Cliquez sur **"Continuer"** puis **"Modifier la base de données"**
4. Attendez que la modification soit terminée (quelques minutes)

---

## 📋 RÉSUMÉ

1. ✅ Trouver votre IP : https://www.whatismyip.com/
2. ✅ Aller dans RDS > mapevent-db > Security Groups
3. ✅ Ajouter une règle pour votre IP (Type: PostgreSQL, Port: 5432)
4. ✅ Attendre 1-2 minutes
5. ✅ Réessayer la connexion

---

**Une fois votre IP autorisée, vous pourrez vous connecter avec pgAdmin !** 🚀


