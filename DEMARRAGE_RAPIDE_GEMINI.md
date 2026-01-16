# ⚡ DÉMARRAGE RAPIDE POUR GEMINI

## 🎯 OBJECTIF IMMÉDIAT

**Corriger le problème de sérialisation** qui fait que le backend renvoie `{"user": "[dict - 17 items]"}` au lieu d'un objet JSON valide.

---

## 📖 LECTURE RAPIDE (5 minutes)

1. **Lire :** `README_GEMINI_COMPLET.md` (section "Problème principal actuel")
2. **Lire :** `RESUME_ETAT_PROJET.md` (section "Problèmes critiques")
3. **Comprendre :** Le problème vient de Flask test client qui transforme les dicts en chaînes

---

## 🔧 CORRECTION RAPIDE (15 minutes)

### Étape 1 : Modifier le Backend

**Fichier :** `lambda-package/backend/main.py`  
**Fonction :** `oauth_google()` (ligne ~1700)

**Chercher :**
```python
response_data = {
    'user': user_data_clean,
    'isNewUser': is_new_user,
    'profileComplete': profile_complete
}
```

**Remplacer par :**
```python
# FORCER la sérialisation de chaque valeur individuellement
user_data_forced = {}
for key, value in user_data_clean.items():
    if isinstance(value, dict):
        user_data_forced[key] = json.loads(json.dumps(value, default=str))
    elif isinstance(value, (list, tuple)):
        user_data_forced[key] = json.loads(json.dumps(value, default=str))
    else:
        user_data_forced[key] = value

response_data = {
    'user': user_data_forced,  # ← Version forcée sérialisée
    'isNewUser': is_new_user,
    'profileComplete': profile_complete
}

# Sérialiser la réponse complète
response_json_str = json.dumps(response_data, ensure_ascii=False, default=str)

# Utiliser Response directement (pas make_response)
from flask import Response
return Response(
    response_json_str,
    mimetype='application/json',
    status=200
)
```

### Étape 2 : Déployer

```powershell
cd lambda-package
python deploy_backend.py
```

### Étape 3 : Tester

1. Ouvrir `https://mapevent.world`
2. Se connecter avec Google
3. Vérifier dans les logs CloudWatch que `user` est un objet JSON valide
4. Vérifier que le formulaire s'affiche

---

## 🐛 SI ÇA NE FONCTIONNE PAS

### Vérifier les logs
```powershell
aws logs tail /aws/lambda/mapevent-backend --follow --region eu-west-1
```

Chercher :
- `✅ user_data sérialisable` : Bon signe
- `⚠️ ATTENTION: user est une chaîne` : Problème persiste
- `🔍 Body brut récupéré` : Voir la réponse brute

### Alternative : Extraire email depuis token Cognito

Dans `lambda-package/handler.py` ligne ~190, ajouter :
```python
# Essayer d'extraire l'email depuis le token Cognito dans les headers
auth_header = headers_lower.get('authorization', '')
if auth_header and auth_header.startswith('Bearer '):
    token = auth_header.replace('Bearer ', '')
    try:
        import base64
        import json as json_lib
        parts = token.split('.')
        if len(parts) >= 2:
            payload = json_lib.loads(base64.urlsafe_b64decode(parts[1] + '=='))
            user_email = payload.get('email', '')
            print(f"🔍 Email extrait depuis token: {user_email}")
    except:
        pass
```

---

## 📞 RESSOURCES

- **Logs CloudWatch :** https://eu-west-1.console.aws.amazon.com/cloudwatch/
- **Console Lambda :** https://eu-west-1.console.aws.amazon.com/lambda/
- **Console API Gateway :** https://eu-west-1.console.aws.amazon.com/apigateway/

---

**Temps estimé :** 30 minutes  
**Difficulté :** Moyenne  
**Priorité :** URGENT







