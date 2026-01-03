# 🔐 Instructions : Autoriser votre IP dans RDS (Français)

## 📍 Vous êtes sur la page de votre base de données `mapevent-db`

### ✅ Ce que vous voyez actuellement :

Dans la section **"Connectivité et sécurité"**, vous voyez :

```
Sécurité
Groupes de sécurité VPC
default (sg-09293e0d6313eb92c)    ← CLIQUEZ ICI !
```

---

## 🎯 Étape par Étape

### Étape 1 : Cliquer sur le Security Group

1. **Trouvez** la ligne qui dit :
   ```
   Groupes de sécurité VPC
   default (sg-09293e0d6313eb92c)
   ```

2. **Cliquez directement sur** `default (sg-09293e0d6313eb92c)`
   - C'est le nom du Security Group
   - En cliquant dessus, vous allez sur la page de configuration du Security Group

---

### Étape 2 : Sur la page du Security Group

Vous allez voir une page avec plusieurs onglets en haut :
- **Details** (Détails)
- **Inbound rules** (Règles entrantes) ← **CLIQUEZ ICI !**
- **Outbound rules** (Règles sortantes)
- **Tags**

---

### Étape 3 : Modifier les Règles Entrantes

1. **Cliquez sur l'onglet** "Inbound rules" (Règles entrantes)
2. Vous verrez les règles actuelles (probablement vide ou avec quelques règles)
3. **Cliquez sur le bouton** "Edit inbound rules" (Modifier les règles entrantes)
   - C'est un bouton en haut à droite, généralement bleu ou orange

---

### Étape 4 : Ajouter votre IP

1. **Cliquez sur** "Add rule" (Ajouter une règle)
2. **Remplissez les champs** :
   
   **Type** :
   - Cliquez sur le menu déroulant
   - Sélectionnez `PostgreSQL`
   - OU tapez `PostgreSQL` dans la recherche
   
   **Protocol** :
   - Devrait être automatiquement `TCP`
   - Si ce n'est pas le cas, sélectionnez `TCP`
   
   **Port range** :
   - Entrez : `5432`
   
   **Source** :
   - Option 1 (Recommandé) : Cliquez sur le menu déroulant et sélectionnez **"My IP"**
     - AWS détecte automatiquement votre IP
   - Option 2 : Sélectionnez "Custom" et entrez votre IP avec `/32`
     - Exemple : `123.45.67.89/32`
     - Trouvez votre IP sur : https://www.whatismyip.com/
   
   **Description** (optionnel) :
   - `Accès administration depuis mon ordinateur`

3. **Vérifiez** que tout est correct :
   - Type : PostgreSQL
   - Protocol : TCP
   - Port : 5432
   - Source : Votre IP (avec /32 si vous l'avez entrée manuellement)

4. **Cliquez sur** "Save rules" (Enregistrer les règles)
   - Bouton en bas à droite, généralement orange ou bleu

---

### Étape 5 : Vérifier

1. **Retournez** sur la page du Security Group
2. **Onglet "Inbound rules"**
3. **Vous devriez voir** votre nouvelle règle :
   ```
   Type: PostgreSQL
   Protocol: TCP
   Port: 5432
   Source: Votre IP/32
   ```

---

## ✅ C'est Fait !

Votre IP est maintenant autorisée à se connecter à RDS.

### Prochaines Étapes

1. **Testez la connexion** avec pgAdmin ou le script Python
2. **Si ça ne marche pas** :
   - Attendez 30 secondes (les règles peuvent prendre du temps)
   - Vérifiez que votre IP est bien celle affichée sur https://www.whatismyip.com/
   - Vérifiez que le port est bien `5432`

---

## 🆘 En Cas de Problème

### Je ne trouve pas "My IP" dans le menu déroulant
- Utilisez l'option "Custom"
- Trouvez votre IP sur https://www.whatismyip.com/
- Entrez-la avec `/32` à la fin (ex: `123.45.67.89/32`)

### Le bouton "Edit inbound rules" est grisé
- Vérifiez que vous avez les permissions nécessaires dans AWS
- Essayez de rafraîchir la page (F5)

### La connexion ne marche toujours pas après avoir ajouté la règle
1. Vérifiez que la règle apparaît bien dans "Inbound rules"
2. Attendez 30-60 secondes
3. Vérifiez votre IP actuelle sur https://www.whatismyip.com/
4. Si votre IP a changé, ajoutez une nouvelle règle avec la nouvelle IP

---

## 📝 Résumé Visuel

```
Page mapevent-db
    ↓
Section "Connectivité et sécurité"
    ↓
"Groupes de sécurité VPC"
    ↓
Cliquez sur "default (sg-09293e0d6313eb92c)"
    ↓
Page Security Group
    ↓
Onglet "Inbound rules"
    ↓
Bouton "Edit inbound rules"
    ↓
"Add rule"
    ↓
Remplir : PostgreSQL, TCP, 5432, Votre IP
    ↓
"Save rules"
    ↓
✅ Terminé !
```

---

**Bon courage ! 🚀**


