# 🚀 Déployer l'API Gateway

## ⚠️ IMPORTANT : Déployer Après Chaque Modification

**Même si vous créez/modifiez une route, elle ne sera PAS accessible tant que l'API n'est pas déployée !**

---

## 📋 Étapes pour Déployer

### 1. Accéder au Menu Actions

1. **Dans API Gateway**, regardez en haut de la page
2. **Cliquez sur "Actions"** (bouton en haut à droite ou menu déroulant)

### 2. Sélectionner "Deploy API"

1. **Dans le menu Actions**, sélectionnez **"Deploy API"**
2. Une fenêtre s'ouvre

### 3. Configurer le Déploiement

1. **Deployment stage :** Sélectionnez `default` (ou le stage que vous utilisez)
2. **Deployment description :** (optionnel) Vous pouvez ajouter une description comme "Ajout route /api/user/likes"
3. **Cliquez sur "Deploy"**

### 4. Attendre le Déploiement

**⏱️ Le déploiement prend quelques secondes.**

Vous verrez un message de confirmation quand c'est fait.

---

## ✅ Vérification

**Après le déploiement :**

1. **Notez l'URL de déploiement** (elle devrait être affichée)
2. **Testez la route** dans votre page de test
3. **Ça devrait fonctionner maintenant !**

---

## 🚨 Important

**Vous devez déployer l'API :**
- ✅ Après avoir créé une nouvelle route
- ✅ Après avoir modifié une route
- ✅ Après avoir configuré CORS
- ✅ Après avoir modifié une intégration Lambda

**Sans déploiement, les modifications ne sont PAS actives !**

---

## 💡 Astuce

**Pour vérifier si l'API est déployée :**
- Regardez en haut de la page API Gateway
- Vous devriez voir le stage actif (ex: "default")
- Si vous voyez "Changes not deployed", il faut déployer !

---

## 📝 Après le Déploiement

**Testez votre route :**
1. Rafraîchissez la page de test (F5)
2. Cliquez sur "Test Likes"
3. Ça devrait fonctionner !



