# ✅ TEST DE CRÉATION DE COMPTE - GUIDE RAPIDE

## 🚀 CORRECTION DÉPLOYÉE

**Date :** 31 décembre 2024, 00:34  
**Status :** ✅ Déployé sur AWS Lambda

---

## 🧪 TEST À FAIRE MAINTENANT

### 1. Ouvrir le site
```
https://mapevent.world
```

### 2. Cliquer sur "Compte"
- La fenêtre de connexion doit s'ouvrir
- **Ne pas voir le champ email directement** (seulement les boutons Google, Facebook, Email)

### 3. Cliquer sur "Connexion avec Google"
- Redirection vers Google
- Autoriser la connexion
- Retour sur le site

### 4. VÉRIFIER DANS LA CONSOLE (F12)
Ouvrir la console du navigateur (F12) et vérifier :

**✅ CE QUI DOIT APPARAÎTRE :**
```javascript
✅ Synchronisation backend réussie - DONNÉES COMPLÈTES: {
  syncData: {
    user: {
      id: "...",
      email: "...",
      username: "...",
      profilePhoto: "...",
      postalAddress: {...}
    },
    profileComplete: true/false,
    isNewUser: true/false
  }
}
```

**❌ CE QUI NE DOIT PAS APPARAÎTRE :**
```javascript
user: "[dict - 17 items]"  // ← PROBLÈME
user: undefined            // ← PROBLÈME
```

### 5. COMPORTEMENT ATTENDU

#### Si NOUVEL utilisateur (première connexion) :
- ✅ Formulaire d'inscription s'affiche
- ✅ Champs pré-remplis avec données Google (email, photo, nom)
- ✅ Remplir : username, mot de passe, adresse postale
- ✅ Cliquer "Créer mon compte"
- ✅ Message "Compte créé avec succès !"
- ✅ Photo et nom apparaissent dans le bloc "Compte"

#### Si utilisateur EXISTANT (déjà inscrit) :
- ✅ **PAS de formulaire d'inscription**
- ✅ Connexion directe
- ✅ Photo et nom apparaissent immédiatement dans le bloc "Compte"

---

## 🔍 VÉRIFICATIONS DÉTAILLÉES

### Vérifier les logs CloudWatch
1. Aller sur : https://eu-west-1.console.aws.amazon.com/cloudwatch/
2. Logs → Log groups → `/aws/lambda/mapevent-backend`
3. Chercher les logs récents
4. Vérifier qu'il n'y a pas d'erreur de sérialisation

### Vérifier la réponse API
Dans la console du navigateur (F12) → Network :
1. Chercher la requête vers `/api/user/oauth/google`
2. Cliquer dessus
3. Onglet "Response"
4. Vérifier que `user` est un objet JSON, pas une chaîne

---

## ❌ SI ÇA NE FONCTIONNE PAS

### Problème : Formulaire ne s'affiche pas
**Solution :** Vérifier la console (F12) pour voir les erreurs

### Problème : `user: "[dict - 17 items]"`
**Solution :** Le problème persiste, vérifier les logs CloudWatch

### Problème : Formulaire s'affiche même après création
**Solution :** Vérifier que `profileComplete: true` est bien renvoyé par le backend

### Problème : Données non sauvegardées
**Solution :** Vérifier la base de données PostgreSQL

---

## 📞 RAPPORT DE TEST

Après avoir testé, noter :

1. ✅ Formulaire s'affiche-t-il pour un nouvel utilisateur ?
2. ✅ Formulaire ne s'affiche-t-il PAS pour un utilisateur existant ?
3. ✅ Les données sont-elles sauvegardées (photo, nom, adresse) ?
4. ✅ Après déconnexion/reconnexion, les données sont-elles toujours là ?
5. ✅ Y a-t-il des erreurs dans la console (F12) ?

---

## 🎯 RÉSULTAT ATTENDU

**Scénario idéal :**
1. Nouvel utilisateur → Formulaire → Création → Photo/Nom affichés
2. Déconnexion → Bouton redevient "Compte"
3. Reconnexion → **PAS de formulaire** → Photo/Nom affichés immédiatement

---

**Bon test ! 🚀**







