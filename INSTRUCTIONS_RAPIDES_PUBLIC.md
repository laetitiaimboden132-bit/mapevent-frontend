# 🚀 INSTRUCTIONS RAPIDES - ACTIVER PUBLIC

## ✅ CE QUE VOUS DEVEZ FAIRE

### 1. Choisir IPv4

**Dans "Type de réseau", choisissez :**
- ✅ **IPv4** (c'est suffisant)

---

### 2. Cliquer sur "Modifier"

**En haut de la page "mapevent-db", cherchez :**
- Un bouton **"Modifier"** (Modify) en haut à droite
- **Cliquez dessus**

---

### 3. Cocher "Accessible publiquement"

**Dans la page de modification :**

1. **Faites défiler** jusqu'à **"Connectivité"**
2. **Cherchez** une case à cocher **"Accessible publiquement"**
3. **Cochez-la** ✅
4. **"Continuer"** → **"Modifier la base de données"**

---

### 4. Attendre 5-10 minutes

**Le statut passera de "Disponible" → "Modification en cours" → "Disponible"**

---

### 5. Ajouter votre IP

**Une fois "Disponible" :**

1. **Trouvez votre IP** : https://www.whatismyip.com/
2. **RDS > mapevent-db > Security Groups > default**
3. **Ajoutez une règle** : Type PostgreSQL, Source = votre IP/32
4. **Attendez 1-2 minutes**
5. **Exécutez** : `python supprimer-comptes.py`

---

**Choisissez IPv4, puis "Modifier" en haut de la page !** 🚀


