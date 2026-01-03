# 📋 Résumé de la Logique des Alertes - Vérification

## ✅ Logique Validée

### 1. **Création de Compte / Avatar**
- ✅ L'utilisateur doit indiquer **au moins une adresse/ville** (max 3)
- ✅ Explication du site lors de la création
- ✅ Explication de pourquoi on demande l'adresse (pour les alertes)
- ✅ Explication du fonctionnement selon l'abonnement

### 2. **Limites d'Alertes**
- ✅ **Gratuit** : 2 alertes max
- ✅ **Avec abonnement** : Illimité (selon les règles d'abonnement)
  - `events-explorer` : Illimité
  - `events-alerts-pro` : Illimité
  - `full-premium` : Illimité
  - `service-pro` / `service-ultra` : Pas d'alertes

### 3. **Alertes Floutées**
- ✅ Si limite atteinte (gratuit = 2), les nouvelles alertes sont **floutées**
- ✅ Les alertes floutées vont quand même dans le bloc "Alertes"
- ✅ L'utilisateur peut effacer une alerte pour en afficher une nouvelle
- ✅ **Avertissement** : Prévenir de noter les infos avant d'effacer
- ✅ Quand on efface une alerte floutée, une nouvelle devient visible

### 4. **Alarmes**
- ✅ Quand une alerte devient floue, l'**alarme correspondante disparaît**
- ✅ Les alarmes ne fonctionnent que pour les alertes visibles (non floutées)

### 5. **Notifications (Mail/SMS)**
- ✅ **Email** : Illimité pour tous les abonnements
- ✅ **SMS** : 
  - Gratuit : 0 SMS
  - `events-explorer` : 10 SMS/mois
  - `events-alerts-pro` : 10 SMS/mois
  - `full-premium` (25.-) : **Illimité**
- ✅ L'utilisateur peut choisir email, SMS, ou les deux

### 6. **Distance**
- ✅ L'alerte n'est créée que si l'événement est à **moins de 75 km** de l'utilisateur
- ✅ Utilisation des adresses définies lors de la création de compte

---

## 🔍 Points à Vérifier

### ✅ Logique Correcte
1. **Limite gratuite = 2 alertes** : ✅ Correct
2. **Alertes floutées quand limite atteinte** : ✅ Correct
3. **Alarmes disparaissent avec alertes floutées** : ✅ Correct
4. **SMS limité sauf premium full** : ✅ Correct
5. **Email illimité** : ✅ Correct

### ⚠️ Points d'Attention
1. **Adresses multiples (max 3)** : L'alerte doit être créée si l'événement est à moins de 75 km d'**au moins une** des adresses
2. **Compteur SMS mensuel** : Doit être réinitialisé chaque mois
3. **Avertissement avant effacement** : Important pour UX

---

## 📝 Implémentation à Faire

1. ✅ Modifier `getAlertLimit()` : Gratuit = 2, Abo = Infinity
2. ✅ Ajouter champ `addresses[]` à `currentUser`
3. ✅ Créer formulaire d'inscription avec demande d'adresse
4. ✅ Implémenter système d'alertes floutées
5. ✅ Implémenter suppression d'alertes avec avertissement
6. ✅ Implémenter système de notifications SMS/Email
7. ✅ Gérer la disparition des alarmes quand alerte devient floue
8. ✅ Modifier la détection pour utiliser les adresses au lieu de `location`

---

## 🎯 Conclusion

**La logique est cohérente et complète !** ✅

Tous les points sont logiques et bien pensés. Je vais maintenant implémenter ces changements.



