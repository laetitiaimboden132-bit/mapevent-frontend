# 🎯 Routes importantes pour le site

## ✅ Route create-tables : PAS utilisée par le site

- `/api/admin/create-tables` = Route **ADMIN**
- Utilisée **une seule fois** pour créer les tables
- **PAS appelée** depuis le site en production
- Le 403 n'est **pas grave** car vous pouvez créer les tables via Lambda directement

## ❌ Route paiement : IMPORTANTE pour le site

- `/api/payments/create-checkout-session` = Route **CRITIQUE**
- **Utilisée par le site** pour les paiements
- **DOIT fonctionner** sinon les paiements ne marcheront pas
- **CORS OBLIGATOIRE** pour que le site puisse l'appeler

## 🔧 Ce qu'il faut faire MAINTENANT

### Pour que le site fonctionne, activez CORS sur la route de paiement :

1. **API Gateway** > Votre API
2. **Ressources** > `/api/payments/create-checkout-session`
3. Sélectionnez la méthode **POST**
4. **Actions** > **"Activer CORS"**
5. Configurez :
   - Origines : `*` (ou `https://mapevent.world`)
   - Méthodes : `POST, OPTIONS`
   - Headers : `Content-Type, Origin`
6. **Déployez l'API** (Actions > Déployer l'API > default)

### C'est cette route qui est importante pour le site !

## ✅ Résumé

- ❌ `/api/admin/create-tables` → 403 pas grave (route admin, pas utilisée par le site)
- ✅ `/api/payments/create-checkout-session` → **DOIT fonctionner** (utilisée par le site)

**Activez CORS sur la route de paiement pour que le site fonctionne !**

