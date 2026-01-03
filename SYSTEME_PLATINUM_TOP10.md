# 🏆 SYSTÈME DE BOOST PLATINUM / TOP 10 - EXPLICATION COMPLÈTE

## 📋 Vue d'ensemble

Le système de boost **Platinum** utilise un mécanisme d'**enchères** pour déterminer les **Top 10** positions les plus visibles sur la carte MapEvent. C'est un système compétitif où les organisateurs/artistes peuvent placer des enchères pour améliorer leur visibilité.

---

## 🎯 Principe de fonctionnement

### 1. **Système de positions (Top 10 illimité)**

- **Top 10 ILLIMITÉ** : Tous ceux qui paient restent dans le Top 10 (pas de limite stricte à 10 personnes)
- Si quelqu'un paie et tombe en bas, il reste dans le Top 10 (pas plus bas que position 10+)
- Plus la position est haute (1 = meilleure), plus la visibilité est importante
- Les positions 1-10 sont les plus visibles, mais il peut y avoir plus de personnes dans le Top 10
- Chaque position a un **prix minimum** :
  - Position 1 : **50 CHF minimum**
  - Position 2 : **45 CHF minimum**
  - Position 3 : **40 CHF minimum**
  - Position 4 : **35 CHF minimum**
  - Position 5 : **30 CHF minimum**
  - Position 6 : **25 CHF minimum**
  - Position 7 : **20 CHF minimum**
  - Position 8 : **15 CHF minimum**
  - Position 9 : **12 CHF minimum**
  - Position 10 : **10 CHF minimum**

### 2. **Mécanisme d'enchères**

#### Comment ça fonctionne :

1. **L'utilisateur clique sur "Enchère Top 10"** dans le popup d'un événement/booking/service
2. **Chargement des positions actuelles** par région depuis le backend (`/api/auction/top10`)
3. **Affichage du modal d'enchères** avec :
   - Position actuelle de l'item (si déjà dans le Top 10)
   - Prix minimums pour chaque position
   - Enchères actuelles pour chaque position
   - Champ pour placer son enchère
   - Option de position souhaitée

4. **L'utilisateur place une enchère** :
   - Il choisit un montant (minimum 10 CHF pour position 10)
   - Optionnellement, il peut choisir une position souhaitée
   - Le système calcule automatiquement la position finale selon le montant

5. **Durée de l'enchère** : **7 jours**
   - L'enchère est active pendant 7 jours
   - L'utilisateur peut l'augmenter à tout moment
   - À l'expiration, il doit renouveler s'il veut rester dans le Top 10

### 3. **Calcul de la position finale**

- La position est déterminée par le **montant de l'enchère**
- Si plusieurs utilisateurs ont le même montant, l'ancienneté de l'enchère prime
- Si quelqu'un place une enchère supérieure, il "dépasse" les autres
- Les positions 1-10 sont constamment mises à jour en temps réel

---

## 💰 Système de paiement

### Processus :

1. **Placement de l'enchère** → Envoi au backend (`POST /api/auction/bid`)
   ```json
   {
     "event_id": 123,
     "event_type": "event", // ou "booking" ou "service"
     "bidder_id": 1,
     "bid_amount": 50.00,
     "desired_position": 1 // optionnel
   }
   ```

2. **Vérification côté backend** :
   - Vérifier que l'utilisateur est connecté
   - Vérifier que le montant est suffisant
   - Vérifier que l'utilisateur a les fonds disponibles
   - Calculer la nouvelle position dans le Top 10

3. **Paiement** :
   - **Prélèvement immédiat** du montant de l'enchère
   - **Stockage de l'enchère** dans la base de données
   - **Mise à jour du Top 10** en temps réel

4. **Confirmation** :
   - Notification de succès avec la position obtenue
   - Mise à jour visuelle immédiate sur la carte

---

## 🎨 Effets visuels sur les marqueurs

**IMPORTANT** : L'intérieur des marqueurs est **TOUJOURS NOIR** (#000000). Seules les **BORDURES** changent de couleur selon le boost.

- Logo catégorie (emoji) : Visible sur fond noir
- Couronne, cœur, étoiles : Visibles sur fond noir
- Bordures : Changent de couleur selon le boost
- AI/Basic (1 CHF) : Bordure noire = invisible (tout noir)

Chaque position dans le Top 10 a des **effets visuels spécifiques** pour attirer l'attention :

### Position 10 (la plus basse)
- Bordure rouge simple
- Taille normale

### Position 9
- Bordure rouge + **1mm plus grand**

### Position 8
- Bordure rouge + **couronne** 👑
- **1mm plus grand**

### Position 7
- Bordure rouge + **0.5mm plus grand**
- Couronne

### Position 6
- Bordure rouge + **pointeur 0.5mm plus grand**
- Couronne

### Position 5
- Bordure rouge + **halo rouge pulsant**
- Couronne

### Position 4
- Bordure rouge + **cœur rouge** ❤️
- Halo rouge

### Position 3
- Bordure rouge + **pointeur et bordure 0.5mm plus épais**
- Cœur rouge

### Position 2
- **Bordure change avec le thème UI** (cyan/bleu/violet selon le thème)
- Halo qui change avec le thème
- Cœur

### Position 1 (LA MEILLEURE !)
- **Bordure ET halo changent avec le thème UI**
- Effets maximaux (couronne, cœur, halo pulsant)
- Taille maximale
- Visibilité maximale

---

## 🌍 Système par région

Le Top 10 est calculé **par région** :

- **CH** (Suisse entière) : Top 10 national
- **Par canton** : BE, ZH, VD, etc. (Top 10 par canton)
- **Ville** : Potentiellement par ville (à implémenter)

Un même événement peut avoir une position différente selon la région :
- Position 1 à Genève
- Position 5 en Suisse entière

---

## 🔄 Renouvellement automatique

- **Expiration après 7 jours**
- L'utilisateur reçoit une notification avant expiration
- Il peut renouveler son enchère à tout moment
- S'il ne renouvelle pas, il sort du Top 10 automatiquement

---

## 💡 Stratégies pour les utilisateurs

1. **Position optimale** : Investir dans une position qui correspond à son budget
2. **Renouvellement proactif** : Renouveler avant expiration pour garder sa position
3. **Augmentation progressive** : Commencer position 10 et augmenter progressivement
4. **Ciblage régional** : Investir dans sa région principale plutôt que national

---

## 🛠️ Implémentation technique

### Frontend (`map_logic.js`) :

```javascript
// Ouverture du modal d'enchères
async function openAuctionModal(type, id)

// Placement d'une enchère
async function submitAuctionBid(type, id)

// Variables globales
let top10Positions = null; // Positions actuelles par région
```

### Backend (à implémenter) :

**Endpoints nécessaires** :
- `GET /api/auction/top10?region=CH` : Récupérer les positions Top 10
- `POST /api/auction/bid` : Placer une enchère
- `GET /api/auction/my-bids` : Voir mes enchères actives
- `PUT /api/auction/bid/:id` : Augmenter une enchère existante

**Base de données** :
- Table `top10_auctions` :
  - `id`, `event_id`, `event_type`, `bidder_id`
  - `bid_amount`, `position`, `region`
  - `created_at`, `expires_at`, `status`

---

## 📊 Exemple concret

**Scénario** : Un événement "Rave Techno" veut être en position 1 à Genève

1. L'organisateur clique sur "Enchère Top 10" dans le popup
2. Le modal s'ouvre, montre que la position 1 à Genève coûte actuellement **52 CHF**
3. L'organisateur place une enchère de **55 CHF** avec position souhaitée = 1
4. Le système prélève 55 CHF immédiatement
5. L'événement apparaît en **position 1** avec tous les effets visuels (bordure + halo qui changent avec le thème, couronne, cœur)
6. Pendant 7 jours, l'événement reste en position 1
7. Avant expiration, l'organisateur reçoit une notification pour renouveler

---

## ✅ Avantages du système

- **Transparent** : Les prix sont clairs et affichés
- **Équitable** : Premier arrivé = première position (si même montant)
- **Flexible** : 10 positions permettent plusieurs niveaux d'investissement
- **Efficace** : Les effets visuels attirent vraiment l'attention
- **Rentable** : Système de revenus récurrents (renouvellement tous les 7 jours)

---

**Ce système est actuellement implémenté côté frontend. Le backend doit être développé pour gérer les enchères, le paiement et le stockage des positions.**

