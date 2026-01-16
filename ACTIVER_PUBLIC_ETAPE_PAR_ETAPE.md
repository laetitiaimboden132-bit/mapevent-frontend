# ✅ ACTIVER "ACCESSIBLE PUBLIQUEMENT" - ÉTAPE PAR ÉTAPE

## 🎯 VOUS ÊTES DANS "CONNECTIVITÉ" - PARFAIT !

### Étape 1 : Choisir IPv4

**Dans "Type de réseau", choisissez :**
- ✅ **IPv4** (pas besoin du mode à double pile pour l'instant)

---

### Étape 2 : Cliquer sur "Modifier"

**En haut de la page de votre base de données "mapevent-db", cherchez :**
- Un bouton **"Modifier"** (Modify) en haut à droite
- **Cliquez dessus**

---

### Étape 3 : Dans la page de modification

**Une nouvelle page s'ouvre avec tous les paramètres modifiables.**

1. **Faites défiler** jusqu'à la section **"Connectivité"**
2. **Dans cette section**, cherchez une case à cocher :
   - **"Accessible publiquement"** (en français)
   - OU **"Publicly accessible"** (en anglais)

---

### Étape 4 : Cocher "Accessible publiquement"

1. **Cochez la case** "Accessible publiquement" ✅
2. **Ne changez rien d'autre !**
3. **Descendez en bas de la page**
4. **Cliquez sur "Continuer"** (Continue)
5. **Dans la page de révision**, cliquez sur **"Modifier la base de données"** (Modify DB instance)

---

### Étape 5 : Attendre

1. **Le statut de votre base va changer** :
   - "Disponible" → "Modification en cours" → "Disponible"
2. **Attendez 5-10 minutes** que la modification soit terminée
3. **Rafraîchissez la page** de temps en temps pour voir le statut

---

### Étape 6 : Après la modification

**Une fois que le statut redevient "Disponible" :**

1. **Vérifiez** que "Accessible publiquement" est maintenant **"Oui"** ✅
2. **Maintenant vous pouvez ajouter la règle** dans le Security Group :
   - RDS > mapevent-db > Security Groups > default
   - Ajoutez votre IP/32 (Type PostgreSQL)
3. **Attendez 1-2 minutes**
4. **Exécutez** : `python supprimer-comptes.py`

---

## ✅ RÉSUMÉ

1. ✅ **Choisissez IPv4** dans "Type de réseau"
2. ✅ **Cliquez sur "Modifier"** (en haut à droite)
3. ✅ **Section "Connectivité"** → **Cochez "Accessible publiquement"**
4. ✅ **"Continuer"** → **"Modifier la base de données"**
5. ⏳ **Attendez 5-10 minutes**
6. ✅ **Ajoutez votre IP** dans le Security Group
7. 🚀 **Exécutez** : `python supprimer-comptes.py`

---

**Choisissez IPv4, puis cliquez sur "Modifier" en haut de la page !** 🚀


