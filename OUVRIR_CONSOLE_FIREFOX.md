# 🦊 Ouvrir la console dans Firefox

## 🎯 Méthode 1 : Raccourci clavier (le plus rapide)

1. **Ouvrez votre site** : https://mapevent.world
2. **Appuyez sur** : `F12` (ou `Ctrl+Shift+K` sur Windows/Linux, `Cmd+Option+K` sur Mac)
3. **La console s'ouvre en bas** de la page

---

## 🎯 Méthode 2 : Menu Firefox

1. **Cliquez sur le menu** (les 3 lignes en haut à droite ☰)
2. **Allez dans** : "Outils de développement web" (ou "Web Developer Tools")
3. **Cliquez sur** : "Console web" (ou "Web Console")

---

## 📍 Où est la console ?

Une fois ouverte, vous verrez :
- **En bas de la page** : Une fenêtre avec des onglets
- **Onglet "Console"** : C'est là qu'il faut taper

---

## ✍️ Comment taper dans la console

1. **Cliquez dans la zone de texte** en bas de la console (là où il y a `>` ou un curseur clignotant)

2. **Tapez exactement** :

```javascript
console.log('Profile Photo:', currentUser.profilePhoto);
```

3. **Appuyez sur Entrée**

4. **Vous devriez voir** quelque chose comme :
   ```
   Profile Photo: https://mapevent-avatars.s3.eu-west-1.amazonaws.com/avatars/user_1767389921855_75fbd18e9395ca09.jpg
   ```
   ou
   ```
   Profile Photo: null
   ```
   ou
   ```
   Profile Photo: undefined
   ```

---

## 🖼️ À quoi ça ressemble

```
┌─────────────────────────────────────────┐
│  Firefox - mapevent.world                 │
├─────────────────────────────────────────┤
│                                           │
│  [Votre page web ici]                    │
│                                           │
├─────────────────────────────────────────┤
│  Console  │  Inspecteur  │  Réseau  │   │  ← ONGLETS
├─────────────────────────────────────────┤
│  > console.log('Profile Photo:', ...)   │  ← ZONE DE TEXTE
│  Profile Photo: https://...               │  ← RÉSULTAT
│                                           │
└─────────────────────────────────────────┘
```

---

## 🆘 Si la console ne s'ouvre pas

### Vérifiez que les outils de développement sont activés :

1. **Menu Firefox** (☰) → **Options** (ou "Préférences")
2. **Section "Général"**
3. **Faites défiler** jusqu'à "Outils de développement"
4. **Cochez** "Activer les outils de développement web"

---

## 📋 Autres commandes utiles

Une fois dans la console, vous pouvez aussi taper :

```javascript
// Voir toutes les infos de l'utilisateur
console.log('Current User:', currentUser);

// Voir juste l'URL de la photo
console.log('Photo URL:', currentUser.profilePhoto);

// Voir l'avatar
console.log('Avatar:', currentUser.avatar);
```

---

## ✅ Checklist

- [ ] J'ai ouvert Firefox
- [ ] J'ai ouvert le site https://mapevent.world
- [ ] J'ai appuyé sur F12 (ou Ctrl+Shift+K)
- [ ] Je vois la console en bas de la page
- [ ] J'ai cliqué dans la zone de texte de la console
- [ ] J'ai tapé la commande
- [ ] J'ai appuyé sur Entrée
- [ ] Je vois le résultat

---

**Dites-moi ce qui s'affiche après avoir tapé la commande !** 😊




