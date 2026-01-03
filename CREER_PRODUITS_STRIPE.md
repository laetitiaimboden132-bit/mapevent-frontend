# 💰 Créer les Produits et Prix dans Stripe - GUIDE COMPLET

## 📍 Étape 0 : Aller dans Stripe

1. **Ouvrir Stripe Dashboard** : https://dashboard.stripe.com
2. **Vérifier le mode** : En haut à droite, vous devez voir **"Mode Live"** (pas "Mode test")
3. **Menu de gauche** : Cliquer sur **"Produits"** (ou "Products" en anglais)
4. **Bouton** : Cliquer sur **"Ajouter un produit"** (ou "Add product") en haut à droite

---

## 🎯 PRODUIT 1 : Events Explorer

### 📝 Informations du Produit

1. **Nom du produit** :
   ```
   Events Explorer
   ```

2. **Description** (optionnel mais recommandé) :
   ```
   10 alertes personnalisées/mois, Agenda 100 places
   ```

### 💰 Tarification

1. **Type de tarification** :
   - ✅ Cocher **"Récurrent"** (ou "Recurring" en anglais)
   - ❌ **NE PAS** cocher "Paiement unique" (ou "One-time")

2. **Prix** :
   - Dans le champ **"Prix"** : `5.00`
   - **Important** : Utiliser un point (`.`) et non une virgule

3. **Devise** :
   - Sélectionner **"CHF"** (Franc suisse)
   - Si vous ne le voyez pas, taper "CHF" dans la recherche

4. **Période de facturation** :
   - Sélectionner **"Mensuel"** (ou "Monthly" en anglais)

### ✅ Enregistrer

1. Cliquer sur **"Enregistrer le produit"** (ou "Save product")
2. Attendre que le produit soit créé

### 📋 Copier l'ID de Prix

1. **Après la création**, le produit s'affiche dans la liste
2. **Cliquer sur le produit** pour voir les détails
3. **Chercher la section "Tarification"** (ou "Pricing")
4. **Vous verrez l'ID de prix** qui ressemble à :
   ```
   price_1ABC123def456ghi789jkl012mno345pqr678
   ```
5. **COPIER CET ID COMPLET** (il commence toujours par `price_`)
6. **📋 Noter quelque part** :
   ```
   STRIPE_PRICE_EVENTS_EXPLORER=price_1ABC123def456ghi789jkl012mno345pqr678
   ```

---

## 🎯 PRODUIT 2 : Events Alertes Pro

### 📝 Informations du Produit

1. **Nom du produit** :
   ```
   Events Alertes Pro
   ```

2. **Description** :
   ```
   Alertes illimitées, Agenda 200 places
   ```

### 💰 Tarification

1. **Type** : ✅ **"Récurrent"**
2. **Prix** : `10.00`
3. **Devise** : `CHF`
4. **Période** : **"Mensuel"**

### ✅ Enregistrer et Copier

1. Cliquer sur **"Enregistrer le produit"**
2. Cliquer sur le produit pour voir les détails
3. **COPIER L'ID DE PRIX** (commence par `price_...`)
4. **📋 Noter** :
   ```
   STRIPE_PRICE_EVENTS_ALERTS_PRO=price_...
   ```

---

## 🎯 PRODUIT 3 : Service Pro

### 📝 Informations du Produit

1. **Nom du produit** :
   ```
   Service Pro
   ```

2. **Description** :
   ```
   Contacts illimités, Badge Pro
   ```

### 💰 Tarification

1. **Type** : ✅ **"Récurrent"**
2. **Prix** : `12.00`
3. **Devise** : `CHF`
4. **Période** : **"Mensuel"**

### ✅ Enregistrer et Copier

1. Cliquer sur **"Enregistrer le produit"**
2. Cliquer sur le produit pour voir les détails
3. **COPIER L'ID DE PRIX** (commence par `price_...`)
4. **📋 Noter** :
   ```
   STRIPE_PRICE_SERVICE_PRO=price_...
   ```

---

## 🎯 PRODUIT 4 : Service Ultra

### 📝 Informations du Produit

1. **Nom du produit** :
   ```
   Service Ultra
   ```

2. **Description** :
   ```
   Tout de Pro + Accès API, 10 events gratuits/mois
   ```

### 💰 Tarification

1. **Type** : ✅ **"Récurrent"**
2. **Prix** : `18.00`
3. **Devise** : `CHF`
4. **Période** : **"Mensuel"**

### ✅ Enregistrer et Copier

1. Cliquer sur **"Enregistrer le produit"**
2. Cliquer sur le produit pour voir les détails
3. **COPIER L'ID DE PRIX** (commence par `price_...`)
4. **📋 Noter** :
   ```
   STRIPE_PRICE_SERVICE_ULTRA=price_...
   ```

---

## 🎯 PRODUIT 5 : Full Premium

### 📝 Informations du Produit

1. **Nom du produit** :
   ```
   Full Premium
   ```

2. **Description** :
   ```
   Tout compris - Agenda 250, Alertes illimitées, Contacts illimités
   ```

### 💰 Tarification

1. **Type** : ✅ **"Récurrent"**
2. **Prix** : `25.00`
3. **Devise** : `CHF`
4. **Période** : **"Mensuel"**

### ✅ Enregistrer et Copier

1. Cliquer sur **"Enregistrer le produit"**
2. Cliquer sur le produit pour voir les détails
3. **COPIER L'ID DE PRIX** (commence par `price_...`)
4. **📋 Noter** :
   ```
   STRIPE_PRICE_FULL_PREMIUM=price_...
   ```

---

## 📋 RÉSUMÉ : Les 5 Produits à Créer

| # | Produit | Prix/mois | Variable Lambda | ID de Prix |
|---|---------|-----------|-----------------|------------|
| 1 | **Events Explorer** | **CHF 5.–** | `STRIPE_PRICE_EVENTS_EXPLORER` | `price_...` |
| 2 | **Events Alertes Pro** | **CHF 10.–** | `STRIPE_PRICE_EVENTS_ALERTS_PRO` | `price_...` |
| 3 | **Service Pro** | **CHF 12.–** | `STRIPE_PRICE_SERVICE_PRO` | `price_...` |
| 4 | **Service Ultra** | **CHF 18.–** | `STRIPE_PRICE_SERVICE_ULTRA` | `price_...` |
| 5 | **Full Premium** | **CHF 25.–** | `STRIPE_PRICE_FULL_PREMIUM` | `price_...` |

---

## ⚠️ POINTS CRITIQUES

### ✅ À Faire ABSOLUMENT

- ✅ **Toujours** cocher **"Récurrent"** (pas "Paiement unique")
- ✅ **Toujours** mettre **"Mensuel"** pour la période
- ✅ **Toujours** utiliser **"CHF"** comme devise
- ✅ **Toujours** copier l'ID de prix complet (commence par `price_...`)
- ✅ Noter chaque ID de prix au fur et à mesure (ne pas attendre la fin)

### ❌ À Ne JAMAIS Faire

- ❌ Ne pas créer de produits avec "Paiement unique"
- ❌ Ne pas oublier de copier les ID de prix
- ❌ Ne pas mélanger les ID de prix entre les produits
- ❌ Ne pas utiliser de virgule dans le prix (utiliser un point : `5.00`)

---

## 🔍 Où Trouver l'ID de Prix (3 Méthodes)

### Méthode 1 : Dans la Liste des Produits

1. Aller dans **Produits** (menu de gauche)
2. Vous voyez la liste de tous vos produits
3. **Cliquer sur un produit**
4. Dans la page de détails, chercher **"Tarification"** (ou "Pricing")
5. L'ID de prix est affiché en petit texte gris
6. Il ressemble à : `price_1ABC123def456ghi789`

### Méthode 2 : Dans les Détails du Produit

1. Cliquer sur le produit
2. Faire défiler jusqu'à la section **"Tarification"**
3. L'ID est affiché à côté du prix
4. Parfois vous pouvez **cliquer directement sur l'ID** pour le copier

### Méthode 3 : Via l'API (Avancé)

Si vous ne trouvez pas l'ID dans l'interface :
1. Aller dans **Développeurs** → **API**
2. Utiliser l'API pour lister les produits
3. Mais normalement, l'interface suffit !

---

## 📝 Après Avoir Créé les 5 Produits

### Étape 1 : Vérifier que Vous Avez les 5 ID

Vous devez avoir noté quelque part :
```
STRIPE_PRICE_EVENTS_EXPLORER=price_...
STRIPE_PRICE_EVENTS_ALERTS_PRO=price_...
STRIPE_PRICE_SERVICE_PRO=price_...
STRIPE_PRICE_SERVICE_ULTRA=price_...
STRIPE_PRICE_FULL_PREMIUM=price_...
```

### Étape 2 : Aller dans AWS Lambda

1. **Ouvrir AWS Console** : https://console.aws.amazon.com
2. **Aller dans Lambda** (chercher "Lambda" dans la barre de recherche)
3. **Sélectionner votre fonction** : `mapevent-backend` (ou le nom de votre fonction)

### Étape 3 : Ajouter les Variables d'Environnement

1. Dans la page de votre fonction Lambda, cliquer sur **"Configuration"** (onglet en haut)
2. Dans le menu de gauche, cliquer sur **"Variables d'environnement"**
3. Cliquer sur **"Modifier"** (bouton en haut à droite)

### Étape 4 : Ajouter les 5 Nouvelles Variables

Vous devez déjà avoir :
- `STRIPE_SECRET_KEY=sk_live_...`
- `STRIPE_PUBLIC_KEY=pk_live_...`

**Ajouter maintenant** (une par une, ou toutes en même temps) :

1. **Cliquer sur "Ajouter une variable d'environnement"**
2. **Clé** : `STRIPE_PRICE_EVENTS_EXPLORER`
3. **Valeur** : `price_...` (votre ID complet)
4. **Répéter pour les 4 autres** :
   - `STRIPE_PRICE_EVENTS_ALERTS_PRO` = `price_...`
   - `STRIPE_PRICE_SERVICE_PRO` = `price_...`
   - `STRIPE_PRICE_SERVICE_ULTRA` = `price_...`
   - `STRIPE_PRICE_FULL_PREMIUM` = `price_...`

### Étape 5 : Enregistrer

1. Cliquer sur **"Enregistrer"** (bouton en bas)
2. Attendre la confirmation

---

## 💡 Astuces pour Aller Plus Vite

### Astuce 1 : Créer Tous les Produits d'un Coup

1. Créer le premier produit (Events Explorer)
2. **Ne pas fermer la page**
3. Cliquer sur **"Ajouter un produit"** à nouveau
4. Créer le deuxième, etc.
5. Noter tous les ID de prix sur un papier/fichier texte
6. Ensuite, les ajouter tous en une fois dans Lambda

### Astuce 2 : Vérification Rapide

Dans Stripe → Produits, vous devez voir :
- ✅ 5 produits au total
- ✅ Chaque produit a un prix récurrent mensuel
- ✅ Chaque prix a un ID qui commence par `price_...`

### Astuce 3 : Si Vous Vous Trompez

- **Produit créé avec le mauvais prix ?** → Vous pouvez modifier le prix dans Stripe
- **Produit créé avec "Paiement unique" ?** → Supprimer le produit et le recréer
- **ID de prix perdu ?** → Cliquer sur le produit dans Stripe, l'ID est toujours visible

---

## ✅ Checklist Complète

### Création des Produits

- [ ] Produit 1 : Events Explorer créé
- [ ] Prix : CHF 5.–/mois (récurrent, mensuel)
- [ ] ID de prix copié : `price_...`
- [ ] Noté quelque part

- [ ] Produit 2 : Events Alertes Pro créé
- [ ] Prix : CHF 10.–/mois (récurrent, mensuel)
- [ ] ID de prix copié : `price_...`
- [ ] Noté quelque part

- [ ] Produit 3 : Service Pro créé
- [ ] Prix : CHF 12.–/mois (récurrent, mensuel)
- [ ] ID de prix copié : `price_...`
- [ ] Noté quelque part

- [ ] Produit 4 : Service Ultra créé
- [ ] Prix : CHF 18.–/mois (récurrent, mensuel)
- [ ] ID de prix copié : `price_...`
- [ ] Noté quelque part

- [ ] Produit 5 : Full Premium créé
- [ ] Prix : CHF 25.–/mois (récurrent, mensuel)
- [ ] ID de prix copié : `price_...`
- [ ] Noté quelque part

### Configuration Lambda

- [ ] AWS Lambda ouvert
- [ ] Fonction `mapevent-backend` sélectionnée
- [ ] Variables d'environnement ouvertes
- [ ] 5 nouvelles variables ajoutées :
  - [ ] `STRIPE_PRICE_EVENTS_EXPLORER`
  - [ ] `STRIPE_PRICE_EVENTS_ALERTS_PRO`
  - [ ] `STRIPE_PRICE_SERVICE_PRO`
  - [ ] `STRIPE_PRICE_SERVICE_ULTRA`
  - [ ] `STRIPE_PRICE_FULL_PREMIUM`
- [ ] Toutes les valeurs enregistrées
- [ ] Lambda sauvegardé

---

## 🆘 Besoin d'Aide ?

### Problème : Je ne trouve pas l'ID de prix

**Solution** :
1. Cliquer sur le produit dans Stripe
2. Chercher dans la section "Tarification" ou "Pricing"
3. L'ID est toujours visible quelque part dans les détails
4. Il commence toujours par `price_`

### Problème : J'ai créé un produit par erreur

**Solution** :
- Vous pouvez le supprimer et le recréer
- Ou modifier le prix existant dans Stripe

### Problème : Je ne vois pas "Produits" dans Stripe

**Solution** :
- Vérifier que vous êtes en **Mode Live** (pas Mode test)
- Le menu peut être en anglais : chercher **"Products"**

### Problème : Je ne peux pas ajouter les variables dans Lambda

**Solution** :
- Vérifier que vous avez les permissions IAM nécessaires
- Essayer de rafraîchir la page
- Vérifier que vous êtes dans la bonne région AWS

---

## 🎯 Prochaine Étape

Une fois les 5 produits créés et les variables ajoutées dans Lambda :

1. ✅ **Produits créés dans Stripe**
2. ✅ **ID de prix copiés**
3. ✅ **Variables ajoutées dans Lambda**
4. ⏭️ **Prochaine étape** : Configurer les Webhooks Stripe

---

**📌 Note** : Gardez ce guide ouvert pendant la création des produits pour ne rien oublier !
