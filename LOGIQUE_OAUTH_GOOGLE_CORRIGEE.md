# ✅ Logique OAuth Google Corrigée

## 📋 Règles de Connexion

### RÈGLE 1 : NOUVEAU COMPTE (`isNewUser = true`)
→ **TOUJOURS** afficher le **formulaire complet** (même si photo présente)

**Pourquoi ?**  
Un nouveau compte doit remplir toutes les informations (nom, prénom, username, photo, adresse, etc.), même si Google a fourni certaines données.

**Exemple :**
- Nouveau compte avec photo Google → Formulaire complet (remplir nom, prénom, username, adresse, etc.)
- Nouveau compte sans photo Google → Formulaire complet (remplir tout, y compris photo)

---

### RÈGLE 2 : COMPTE EXISTANT (`isNewUser = false`)
→ Demander **SEULEMENT** les données manquantes

**Pourquoi ?**  
Un compte existant (créé avant les modifications) a déjà certaines informations. On demande seulement ce qui manque.

**Exemples :**
- Compte existant avec photo mais sans adresse → Pas de formulaire (adresse optionnelle)
- Compte existant sans photo → **Formulaire photo uniquement**
- Compte existant complet → Connexion directe
- Compte existant avec plusieurs données manquantes → Formulaire adapté (photo uniquement si c'est la seule, sinon formulaire complet pré-rempli)

---

## 🔄 Flux Complet

### Scenario 1 : Nouveau Compte avec Photo Google
1. Utilisateur se connecte via Google OAuth
2. Backend détecte : `isNewUser = true` (compte n'existe pas)
3. Backend crée le compte avec données Google
4. Frontend reçoit : `isNewUser: true`
5. **Frontend affiche : Formulaire complet** (toujours pour nouveau compte)
6. Utilisateur remplit le formulaire (nom, prénom, username, confirme photo, adresse, etc.)
7. Email de confirmation envoyé après validation du formulaire

### Scenario 2 : Nouveau Compte sans Photo Google
1. Utilisateur se connecte via Google OAuth
2. Backend détecte : `isNewUser = true` (compte n'existe pas)
3. Backend crée le compte avec données Google (sans photo)
4. Frontend reçoit : `isNewUser: true`, `missingData: ['photo']`
5. **Frontend affiche : Formulaire complet** (toujours pour nouveau compte)
6. Utilisateur remplit le formulaire (tout, y compris photo obligatoire)
7. Email de confirmation envoyé après validation du formulaire

### Scenario 3 : Compte Existant Complet
1. Utilisateur se connecte via Google OAuth
2. Backend détecte : `isNewUser = false` (compte existe déjà)
3. Backend récupère les données existantes
4. Frontend reçoit : `isNewUser: false`, `profileComplete: true`, `missingData: []`
5. **Frontend affiche : Connexion directe** (aucun formulaire)
6. Utilisateur connecté immédiatement

### Scenario 4 : Compte Existant - Photo Manquante
1. Utilisateur se connecte via Google OAuth
2. Backend détecte : `isNewUser = false` (compte existe déjà)
3. Backend vérifie : photo manquante
4. Frontend reçoit : `isNewUser: false`, `profileComplete: false`, `missingData: ['photo']`
5. **Frontend affiche : Formulaire photo uniquement** (seulement la photo)
6. Utilisateur upload sa photo
7. Compte mis à jour et connexion

### Scenario 5 : Compte Existant - Plusieurs Données Manquantes
1. Utilisateur se connecte via Google OAuth
2. Backend détecte : `isNewUser = false` (compte existe déjà)
3. Backend vérifie : plusieurs données manquantes
4. Frontend reçoit : `isNewUser: false`, `missingData: ['photo', 'adresse']`
5. **Frontend affiche : Formulaire complet pré-rempli** (toutes les données)
6. Utilisateur complète les informations manquantes
7. Compte mis à jour et connexion

---

## 📝 Code Frontend (`map_logic.js`)

```javascript
// RÈGLE 1: NOUVEAU COMPTE → TOUJOURS FORMULAIRE COMPLET
if (isNewUser) {
  // Afficher formulaire complet, pré-rempli avec données Google
  showProRegisterForm();
  // Pré-remplir registerData avec syncData.user
  return;
}

// RÈGLE 2: COMPTE EXISTANT → SEULEMENT CE QUI MANQUE
// CAS 1: Profil complet → Connexion directe
if (profileComplete && missingData.length === 0) {
  // Connexion directe, aucun formulaire
  updateAuthUI(slimUser);
  return;
}

// CAS 2: Données manquantes → Demander seulement ce qui manque
if (missingData.length > 0) {
  if (missingData.length === 1 && missingData[0] === 'photo') {
    // Photo uniquement manquante → Formulaire photo uniquement
    showPhotoUploadForm(syncData.user);
  } else {
    // Plusieurs données manquantes → Formulaire complet pré-rempli
    showProRegisterForm();
  }
  return;
}
```

---

## 🔍 Vérification Backend (`main.py`)

Le backend doit retourner :
- `isNewUser: true/false` → Indique si c'est un nouveau compte
- `profileComplete: true/false` → Indique si le profil est complet
- `missingData: []` → Liste des données manquantes (ex: `['photo']`)

```python
# Backend vérifie si compte existe
cursor.execute("SELECT id FROM users WHERE email_canonical = %s OR google_sub = %s", ...)
user_row = cursor.fetchone()

if user_row:
    # Compte existant
    is_new_user = False
    # Vérifier données manquantes
    missing_data = []
    if not has_photo:
        missing_data.append('photo')
    # ...
else:
    # Nouveau compte
    is_new_user = True
    # Créer le compte
    # ...

# Retourner dans la réponse
payload = {
    'ok': True,
    'isNewUser': bool(is_new_user),
    'profileComplete': bool(profile_complete),
    'missingData': missing_data if 'missing_data' in locals() else [],
    'user': user_slim
}
```

---

## ✅ Checklist

- [x] Frontend vérifie `isNewUser` en premier
- [x] Si `isNewUser = true` → Toujours afficher formulaire complet
- [x] Si `isNewUser = false` → Vérifier `missingData`
- [x] Si `missingData` contient seulement `'photo'` → Formulaire photo uniquement
- [x] Si `missingData` contient plusieurs éléments → Formulaire complet pré-rempli
- [x] Backend retourne correctement `isNewUser`
- [x] Backend retourne correctement `missingData`

---

## 🎉 C'est Corrigé !

La logique est maintenant conforme à vos attentes :
- **Nouveau compte** → Formulaire complet (toujours)
- **Compte existant** → Seulement ce qui manque
