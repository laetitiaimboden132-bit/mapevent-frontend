# 🔧 Corriger la réponse de méthode dans API Gateway

## 🔍 Problème
Les logs Lambda montrent START et END mais pas de logs intermédiaires. La requête arrive à Lambda mais la réponse n'est peut-être pas correctement configurée dans API Gateway.

## ✅ Solution : Configurer la réponse de méthode

### Étape 1 : Vérifier la réponse de méthode

1. **API Gateway** > Votre API
2. **Ressources** > `/api/admin/create-tables` > Méthode **POST**
3. Cliquez sur **"Réponse de méthode"** (Method Response) dans le panneau de gauche
4. Vous devriez voir une liste de codes de statut HTTP

### Étape 2 : Ajouter le code 200 si absent

1. Si le code **200** n'est pas présent :
   - Cliquez sur **"Ajouter une réponse de modèle"** ou **"Add Response Model"**
   - Code de statut HTTP : **200**
   - Cliquez sur **"✓"** pour sauvegarder

2. Si le code **200** est présent :
   - Cliquez dessus
   - Vérifiez les modèles de réponse :
     - **Content-Type** : `application/json`
     - **Modèle** : (peut être vide avec Lambda Proxy)

### Étape 3 : Vérifier la réponse d'intégration

1. Cliquez sur **"Réponse d'intégration"** (Integration Response) dans le panneau de gauche
2. Avec Lambda Proxy integration, cela devrait être automatique
3. Vérifiez qu'il n'y a pas d'erreur

### Étape 4 : Vérifier le format de la réponse Lambda

Avec Lambda Proxy, Lambda doit retourner :
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
  },
  "body": "{\"status\":\"success\"}"
}
```

Mais Flask avec Lambda Proxy devrait gérer cela automatiquement.

## 🔍 Diagnostic : Ajouter des logs dans le code

Pour voir si la route est bien appelée, ajoutez des logs dans `admin_routes.py` :

```python
@app.route('/api/admin/create-tables', methods=['POST'])
def create_tables():
    logger.info("🔧 Route create-tables appelée")  # Ajoutez cette ligne
    try:
        logger.info("📋 Lecture du fichier schema.sql")  # Ajoutez cette ligne
        # ... reste du code
```

Puis redéployez Lambda et retestez. Vous devriez voir ces logs dans CloudWatch.

## ✅ Solution rapide : Vérifier la structure de la route

1. **API Gateway** > Votre API
2. **Ressources**
3. Vérifiez la structure exacte :
   ```
   /api
     /admin
       /create-tables
         POST
   ```

4. Vérifiez que vous testez la bonne URL :
   ```
   https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/admin/create-tables
   ```
   (pas `/default/api/admin/create-tables`)

## 🚨 Solution alternative : Recréer la route

Si rien ne fonctionne, recréez la route :

1. **Supprimez** la méthode POST de `/create-tables`
2. **Recréez** la méthode POST
3. **Configurez** l'intégration Lambda
4. **Activez CORS**
5. **Déployez**

## 📋 Checklist

- [ ] Réponse de méthode : Code 200 présent
- [ ] Réponse d'intégration : Configurée
- [ ] URL de test : Correcte (sans `/default`)
- [ ] Logs Lambda : Vérifiés (ajoutez des logs si nécessaire)
- [ ] API déployée

