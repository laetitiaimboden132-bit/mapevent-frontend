# 📋 Plan d'implémentation : Système d'Alertes et d'Alarmes

## ✅ Déjà implémenté

1. ✅ `checkFavoritesInNewEvents()` - Détection des favoris dans nouveaux événements avec vérification distance 75km
2. ✅ `showAlertsLoginPopup()` - Popup d'alertes au login
3. ✅ `openAlertsView()` - Vue des alertes
4. ✅ `refreshAlertsView()` - Rafraîchissement de la vue
5. ✅ `buildAlertCard()` - Carte d'alerte avec support flouté
6. ✅ `openEventFromAlert()` - Ouvrir événement depuis alerte
7. ✅ `openAddAlarmModal()` - Modal d'ajout d'alarme
8. ✅ `saveAlarm()` - Sauvegarde d'alarme
9. ✅ `loadUserDataOnLogin()` - Chargement des données utilisateur
10. ✅ Système d'alertes floutées (logique dans `checkFavoritesInNewEvents`)
11. ✅ Gestion des limites d'alertes selon abonnement (`getAlertLimit()`)
12. ✅ Gestion des limites SMS selon abonnement (`getSMSLimit()`, `canSendSMS()`)

## ❌ À implémenter

### 1. Backend - Endpoints `/api/user/alerts`
- [ ] `GET /api/user/alerts?userId=X` - Récupérer les alertes d'un utilisateur
- [ ] `POST /api/user/alerts` - Créer une alerte
- [ ] `POST /api/user/alerts/seen` - Marquer une alerte comme vue
- [ ] `DELETE /api/user/alerts` - Supprimer une alerte

### 2. Frontend - Fonctions manquantes
- [ ] `deleteAlertWithWarning()` - Supprimer une alerte avec avertissement si floutée
- [ ] `checkAndTriggerAlarms()` - Vérifier et déclencher les alarmes (email/SMS)
- [ ] `updateSmsCount()` - Mettre à jour le compteur SMS mensuel
- [ ] `openRegisterModal()` - Modal d'inscription 3 étapes
- [ ] `showRegisterStep1()` - Étape 1 : Explication du site
- [ ] `showRegisterStep2()` - Étape 2 : Informations personnelles
- [ ] `showRegisterStep3()` - Étape 3 : Adresses (max 3) avec explication alertes
- [ ] `addAddressField()` - Ajouter un champ d'adresse
- [ ] `removeAddressField()` - Retirer un champ d'adresse
- [ ] `geocodeAddress()` - Géocoder une adresse (Nominatim)
- [ ] `completeRegistration()` - Finaliser l'inscription

### 3. Intégration
- [ ] Appeler `checkAndTriggerAlarms()` périodiquement ou au chargement
- [ ] Intégrer le formulaire d'inscription dans `openLoginModal()`
- [ ] Vérifier que `loadUserDataOnLogin()` charge bien les adresses

## 📝 Ordre d'implémentation recommandé

1. **Backend endpoints** (priorité haute)
   - Permet de sauvegarder/charger les alertes
   - Nécessaire pour la persistance

2. **Fonctions d'inscription** (priorité haute)
   - Permet aux utilisateurs de créer un compte avec adresses
   - Nécessaire pour le système d'alertes (distance 75km)

3. **`deleteAlertWithWarning()`** (priorité moyenne)
   - Permet de supprimer des alertes avec avertissement
   - Améliore l'UX

4. **`checkAndTriggerAlarms()` et `updateSmsCount()`** (priorité moyenne)
   - Permet de déclencher les notifications
   - Peut être simulé dans un premier temps

5. **Tests complets** (priorité basse)
   - Tester le flux complet : inscription → favoris → alertes → alarmes



