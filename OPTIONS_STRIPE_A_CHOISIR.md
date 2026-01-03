# ✅ Options Stripe à Choisir pour MapEventAI

## 🎯 Options à Sélectionner (OBLIGATOIRE)

### 1. ✅ **Paiements non récurrents** 
**POURQUOI :** 
- Achat de contacts (CHF 1.–)
- Panier (plusieurs contacts)
- Donations Mission Planète

**DÉJÀ IMPLÉMENTÉ :** Oui, dans notre code

---

### 2. ✅ **Paiements récurrents**
**POURQUOI :**
- Abonnements mensuels (CHF 5.– à 25.–/mois)
- Events Explorer, Events Alertes Pro, Service Pro, etc.

**DÉJÀ IMPLÉMENTÉ :** Oui, dans notre code

---

## 🔮 Option à Sélectionner (OPTIONNEL - Plus tard)

### 3. ⚠️ **Création de plateforme ou de marketplace**
**POURQUOI :**
- Permettre aux organisateurs de vendre leurs événements
- Permettre aux artistes de vendre leurs services
- MapEventAI prend une commission

**QUAND :** Plus tard, quand le système de base fonctionne bien

**DÉJÀ IMPLÉMENTÉ :** Non, mais le guide existe dans `GUIDE_PAIEMENTS_ET_MARKETPLACE.md`

---

## ❌ Options à NE PAS Sélectionner (Pour l'instant)

### ❌ Factures
- Pas nécessaire pour l'instant
- On utilise Stripe Checkout (pas besoin de factures manuelles)

### ❌ Collecte de taxes
- Peut être ajouté plus tard si nécessaire
- Pour l'instant, les prix sont TTC

### ❌ Paiements par TPE (Terminal de paiement)
- Pas nécessaire (tout est en ligne)

### ❌ Vérification d'identité
- Pas nécessaire pour les clients
- Stripe vérifie automatiquement les cartes

### ❌ Contributions à Climate
- Optionnel, peut être ajouté plus tard

### ❌ Protection contre la fraude
- Stripe gère automatiquement (Radar)
- Pas besoin d'activer séparément

### ❌ Accès aux données bancaires
- Pas nécessaire pour l'instant

### ❌ Me connecter à une entreprise qui utilise Stripe
- Pas applicable (vous créez votre propre compte)

### ❌ Émission de cartes
- Pas nécessaire (on accepte les paiements, on n'émet pas de cartes)

### ❌ Services financiers
- Pas nécessaire pour l'instant

---

## 📋 Résumé : Ce qu'il faut cocher

**Cochez UNIQUEMENT :**
1. ✅ **Paiements non récurrents**
2. ✅ **Paiements récurrents**

**Optionnel (pour plus tard) :**
3. ⚠️ **Création de plateforme ou de marketplace** (si vous voulez préparer l'avenir)

---

## 💡 Recommandation

**Pour commencer rapidement :**
- Cochez **seulement** les 2 premières options
- Vous pourrez ajouter la marketplace plus tard
- Moins de complexité = plus rapide à configurer

**Après avoir coché, vous pourrez :**
- Obtenir vos clés API
- Créer les produits/prix
- Tester le système
- Ajouter d'autres fonctionnalités plus tard si besoin

---

## 🚀 Prochaines Étapes

Une fois les options sélectionnées :

1. **Obtenir les clés API**
   - Publishable key (`pk_test_...`)
   - Secret key (`sk_test_...`)

2. **Créer les produits/prix**
   - Events Explorer : CHF 5.–/mois
   - Events Alertes Pro : CHF 10.–/mois
   - Service Pro : CHF 12.–/mois
   - Service Ultra : CHF 18.–/mois
   - Full Premium : CHF 25.–/mois

3. **Configurer les variables d'environnement Lambda**
   - Voir `CONFIGURATION_STRIPE.md`

4. **Tester avec des cartes de test**
   - Carte test : `4242 4242 4242 4242`



