# ✅ RÉSUMÉ ULTRA SIMPLE POUR GEMINI

## 🎯 CE QUE GEMINI A BESOIN DE SAVOIR

### Le Problème
Le backend renvoie `{"user": "[dict - 17 items]"}` au lieu d'un objet JSON valide.

### La Solution
Forcer la sérialisation dans `lambda-package/backend/main.py` fonction `oauth_google()` ligne ~1700.

### Les Chemins AWS (TOUT EST DANS RESUME_CHEMINS_AWS.md)
- **API Gateway :** `j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default`
- **Lambda :** `mapevent-backend` (région eu-west-1)
- **RDS :** `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com:5432`
- **Redis :** `mapevent-cache-0001-001.mapevent-cache.jqxmjs.euw1.cache.amazonaws.com:6379`
- **Cognito :** `eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`
- **Site :** `https://mapevent.world`

### Fichiers à Modifier
1. `lambda-package/backend/main.py` (ligne ~1700)
2. `public/map_logic.js` (ligne ~380) - Simplifier la logique

### Déployer
```powershell
cd lambda-package
python deploy_backend.py
```

### Voir les Logs
```powershell
aws logs tail /aws/lambda/mapevent-backend --follow --region eu-west-1
```

---

**C'EST TOUT !** Gemini peut lire les fichiers de documentation pour plus de détails.







