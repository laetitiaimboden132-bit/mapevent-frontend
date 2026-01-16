# Déploiement avec Cache-Bust - Instructions

## ✅ Modifications effectuées

1. **Cache-bust statique dans `mapevent.html`** :
   - Remplacement du cache-bust dynamique (`new Date().getTime()`) par un cache-bust statique
   - Nouveau : `<script src="map_logic.js?v=20260107-1"></script>`

2. **Script de déploiement mis à jour** :
   - `deploy-frontend.ps1` invalide maintenant spécifiquement :
     - `/map_logic.js*`
     - `/mapevent.html*`
     - `/index.html*`

## 🚀 Déploiement

### Étape 1 : Vérifier les fichiers

```powershell
cd C:\MapEventAI_NEW\frontend
dir public\map_logic.js
dir public\mapevent.html
```

### Étape 2 : Déployer vers S3 et invalider CloudFront

```powershell
.\deploy-frontend.ps1
```

Le script va :
1. Uploader tous les fichiers du dossier `public/` vers S3 (`mapevent-frontend-laetibibi`)
2. Invalider CloudFront pour les chemins spécifiques
3. Attendre la completion de l'invalidation

### Étape 3 : Vérifier le déploiement

Ouvrir https://mapevent.world dans un navigateur et dans la console (F12) :

```javascript
typeof openAuthModal
```

**Résultat attendu** : `"function"`

Si ce n'est pas le cas :
1. Vider le cache du navigateur (Ctrl+Shift+Delete)
2. Vérifier que l'invalidation CloudFront est terminée
3. Recharger la page en forçant le rechargement (Ctrl+F5)

## 📝 Configuration

- **S3 Bucket** : `mapevent-frontend-laetibibi`
- **CloudFront Distribution ID** : `EMB53HDL7VFIJ`
- **Région** : `eu-west-1`

## 🔄 Pour mettre à jour le cache-bust à l'avenir

Modifier la version dans `public/mapevent.html` :
```html
<script src="map_logic.js?v=20260107-2"></script>
```

Puis redéployer avec `.\deploy-frontend.ps1`



