# ✅ Checklist de Test - mapevent.world

## 🔍 Points à vérifier

### 1. Chargement de la page
- [ ] La page se charge sans erreurs dans la console
- [ ] La carte Leaflet s'affiche correctement
- [ ] Pas d'erreurs 404 pour les fichiers JS

### 2. Fonctionnalités principales
- [ ] **Carte** : Affichage des événements/bookings/services
- [ ] **Filtres** : Filtrage par catégories fonctionne
- [ ] **Recherche** : Recherche de villes fonctionne
- [ ] **Popups** : Clic sur un marqueur affiche la popup

### 3. Authentification
- [ ] **Connexion Google** : Le bouton de connexion fonctionne
- [ ] **Profil** : Affichage du profil utilisateur
- [ ] **Déconnexion** : Fonctionne correctement

### 4. Fonctionnalités utilisateur
- [ ] **Favoris** : Ajout/suppression de favoris
- [ ] **Agenda** : Ajout d'événements à l'agenda
- [ ] **Notifications** : Les notifications toast s'affichent

### 5. Console du navigateur
- [ ] Pas d'erreurs JavaScript
- [ ] Pas d'erreurs CORS
- [ ] Pas d'erreurs de réseau (404, 500, etc.)

### 6. Performance
- [ ] Chargement rapide de la page
- [ ] Pas de ralentissements visibles
- [ ] Animations fluides

## 🐛 En cas de problème

### Erreurs courantes

1. **Erreur 404 pour un fichier JS**
   - Vérifier que tous les fichiers sont déployés
   - Vérifier les chemins dans mapevent.html

2. **Erreur CORS**
   - Vérifier la configuration CORS du backend
   - Utiliser `verifier-cors.py` pour vérifier

3. **Erreur "function is not defined"**
   - Vérifier l'ordre de chargement des scripts
   - Vérifier que auth.js est chargé avant map_logic.js

4. **La carte ne s'affiche pas**
   - Vérifier la connexion internet
   - Vérifier que Leaflet.js se charge correctement

## 📝 Notes

- Les nouveaux modules (`config.js`, `utils.js`, etc.) ne sont **pas encore chargés** dans le HTML
- Le code existant fonctionne toujours avec les fonctions globales
- Les optimisations sont prêtes pour une future migration progressive

## ✅ Après le test

Si tout fonctionne :
- ✅ Le site est opérationnel
- ✅ Les optimisations n'ont pas cassé le code existant
- ✅ Prêt pour développement futur

Si des problèmes :
- Noter les erreurs dans la console
- Vérifier les fichiers manquants
- Corriger les problèmes identifiés
