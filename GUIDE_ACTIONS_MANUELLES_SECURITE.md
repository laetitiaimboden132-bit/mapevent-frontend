# 📋 GUIDE PAS À PAS - ACTIONS MANUELLES SÉCURITÉ

## 🎯 OBJECTIF

Finaliser la configuration de sécurité niveau leader mondial en 2 étapes simples (10 minutes).

---

## ✅ ÉTAPE 1 : S'ABONNER AUX ALERTES SNS (5 minutes)

### Pourquoi ?
Recevoir des alertes par email/SMS en cas d'attaque ou d'activité suspecte sur votre système.

### Comment faire ?

#### 1.1 Ouvrir AWS Console
1. Allez sur : https://console.aws.amazon.com
2. Connectez-vous avec vos identifiants AWS
3. Assurez-vous d'être dans la région **eu-west-1** (Irlande)

#### 1.2 Accéder à SNS
1. Dans la barre de recherche en haut, tapez : **SNS**
2. Cliquez sur **Simple Notification Service**
3. Dans le menu de gauche, cliquez sur **Topics**

#### 1.3 Trouver le topic
1. Vous devriez voir un topic nommé : **mapevent-security-alerts**
2. Cliquez dessus pour l'ouvrir

#### 1.4 Créer un abonnement
1. Cliquez sur le bouton **Create subscription** (en haut à droite)
2. **Protocol** : Sélectionnez **Email** (ou **SMS** si vous préférez)
3. **Endpoint** : Entrez votre adresse email (ou numéro de téléphone pour SMS)
   - Exemple : `votre.email@gmail.com`
4. Cliquez sur **Create subscription**

#### 1.5 Confirmer l'abonnement
1. **IMPORTANT** : Vérifiez votre boîte email
2. Vous devriez recevoir un email de confirmation AWS SNS
3. Cliquez sur le lien dans l'email pour confirmer
4. Vous verrez "Subscription confirmed" ✅

#### ✅ Vérification
- Retournez dans AWS Console > SNS > Topics > mapevent-security-alerts
- Vous devriez voir votre abonnement avec le statut **Confirmed** (vert)

**🎉 Étape 1 terminée ! Vous recevrez maintenant des alertes en cas d'attaque.**

---

## ✅ ÉTAPE 2 : ASSOCIER SECURITY HEADERS À CLOUDFRONT (5 minutes)

### Pourquoi ?
Activer les headers de sécurité HTTP (HSTS, X-Frame-Options, etc.) pour protéger contre XSS, clickjacking, etc.

### Comment faire ?

#### 2.1 Ouvrir CloudFront
1. Dans la barre de recherche AWS, tapez : **CloudFront**
2. Cliquez sur **CloudFront**
3. Vous devriez voir votre distribution : **EMB53HDL7VFIJ**

#### 2.2 Ouvrir la distribution
1. Cliquez sur l'ID de la distribution : **EMB53HDL7VFIJ**
2. Attendez que la page se charge complètement

#### 2.3 Accéder aux Behaviors
1. Cliquez sur l'onglet **Behaviors** (en haut)
2. Vous devriez voir au moins un behavior (souvent le premier avec `*` comme Path Pattern)

#### 2.4 Éditer le behavior
1. **Sélectionnez le premier behavior** (celui avec `*` comme Path Pattern)
2. Cliquez sur **Edit** (ou double-cliquez sur le behavior)

#### 2.5 Associer la Response Headers Policy
1. Descendez jusqu'à la section **Response headers policy**
2. Cliquez sur le menu déroulant
3. Sélectionnez : **mapevent-security-headers-policy**
   - Si vous ne la voyez pas, tapez "mapevent" dans la recherche
4. Descendez en bas de la page
5. Cliquez sur **Save changes**

#### 2.6 Attendre la propagation
1. CloudFront va mettre à jour la distribution
2. **Statut** : En haut de la page, vous verrez "In Progress"
3. **Temps estimé** : 5-15 minutes
4. Vous pouvez fermer la page, ça se fera en arrière-plan

#### ✅ Vérification (après 5-15 minutes)
1. Retournez dans CloudFront > Distribution > EMB53HDL7VFIJ
2. Onglet **Behaviors**
3. Vérifiez que le behavior a bien **mapevent-security-headers-policy** dans la colonne "Response headers policy"

**🎉 Étape 2 terminée ! Les Security Headers sont maintenant actifs.**

---

## 🎯 RÉSUMÉ

### ✅ Ce qui est fait automatiquement
- ✅ Secrets Manager : 4 secrets créés et intégrés dans le code
- ✅ CloudWatch Alarms : 3 alarmes créées
- ✅ Security Headers Policy : Créée et prête

### ⚠️ Ce que vous devez faire (10 minutes)
1. ✅ **S'abonner au topic SNS** (5 min) → Recevoir les alertes
2. ✅ **Associer la policy à CloudFront** (5 min) → Activer les Security Headers

---

## 🆘 EN CAS DE PROBLÈME

### Si vous ne trouvez pas le topic SNS
- Vérifiez que vous êtes dans la région **eu-west-1**
- Le topic devrait s'appeler exactement : **mapevent-security-alerts**

### Si vous ne trouvez pas la Response Headers Policy
- Vérifiez que vous êtes dans la région **us-east-1** (CloudFront est global)
- Ou cherchez "mapevent" dans le menu déroulant

### Si CloudFront ne se met pas à jour
- Attendez 15-20 minutes
- Vérifiez qu'il n'y a pas d'erreur dans l'onglet "Error pages"

---

## 📞 BESOIN D'AIDE ?

Si vous êtes bloqué à une étape, dites-moi :
- À quelle étape vous êtes
- Ce que vous voyez à l'écran
- Le message d'erreur (s'il y en a un)

Je vous guiderai pas à pas ! 🚀
