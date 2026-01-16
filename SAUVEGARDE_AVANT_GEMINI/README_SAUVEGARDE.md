# 💾 SAUVEGARDE AVANT GEMINI

**Date de sauvegarde :** 31 décembre 2024  
**Raison :** Sauvegarde avant que Gemini modifie le code

---

## 📁 FICHIERS SAUVEGARDÉS

### Frontend
- `mapevent.html` : Page principale HTML
- `map_logic.js` : Logique JavaScript complète (~20000 lignes)

### Backend
- `handler.py` : Handler Lambda principal
- `lambda_function.py` : Point d'entrée Lambda
- `backend_main.py` : Application Flask (route oauth_google)
- `requirements.txt` : Dépendances Python
- `deploy_backend.py` : Script de déploiement

---

## 🔄 COMMENT RESTAURER

### Si Gemini détruit le code

#### Restaurer le Frontend
```powershell
Copy-Item -Path "SAUVEGARDE_AVANT_GEMINI\mapevent.html" -Destination "public\mapevent.html" -Force
Copy-Item -Path "SAUVEGARDE_AVANT_GEMINI\map_logic.js" -Destination "public\map_logic.js" -Force
```

#### Restaurer le Backend
```powershell
Copy-Item -Path "SAUVEGARDE_AVANT_GEMINI\handler.py" -Destination "lambda-package\handler.py" -Force
Copy-Item -Path "SAUVEGARDE_AVANT_GEMINI\lambda_function.py" -Destination "lambda-package\lambda_function.py" -Force
Copy-Item -Path "SAUVEGARDE_AVANT_GEMINI\backend_main.py" -Destination "lambda-package\backend\main.py" -Force
Copy-Item -Path "SAUVEGARDE_AVANT_GEMINI\requirements.txt" -Destination "lambda-package\backend\requirements.txt" -Force
Copy-Item -Path "SAUVEGARDE_AVANT_GEMINI\deploy_backend.py" -Destination "lambda-package\deploy_backend.py" -Force
```

#### Redéployer après restauration
```powershell
cd lambda-package
python deploy_backend.py
```

---

## ⚠️ ATTENTION

- **NE PAS restaurer `lambda.env`** : Contient les mots de passe
- **Vérifier les modifications** : Gemini peut avoir fait des améliorations
- **Tester avant de restaurer** : Vérifier que Gemini a vraiment cassé quelque chose

---

## 📝 NOTES

Cette sauvegarde contient l'état du code AVANT que Gemini le modifie.  
Si Gemini améliore le code, ne pas restaurer cette sauvegarde.  
Utiliser uniquement si Gemini casse quelque chose d'important.

---

**Date de création :** 31 décembre 2024







