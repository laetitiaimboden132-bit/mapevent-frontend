# Tests du Composant Adresse Mondiale

## ✅ État actuel

### Backend
- ✅ Migration SQL exécutée avec succès
- ✅ Colonnes d'adresse ajoutées dans `users` :
  - `address_label` VARCHAR(500)
  - `address_lat` DECIMAL(10, 8)
  - `address_lng` DECIMAL(11, 8)
  - `address_country_code` VARCHAR(2)
  - `address_city` VARCHAR(100)
  - `address_postcode` VARCHAR(20)
  - `address_street` VARCHAR(200)
- ✅ Index créé sur `(address_lat, address_lng)`
- ✅ Table `user_alert_settings` créée
- ✅ Endpoint `PUT /api/user/address` déployé
- ✅ Endpoint `GET /api/user/me` modifié pour retourner `address`

### Frontend
- ✅ Composant autocomplete OpenStreetMap/Nominatim implémenté
- ✅ Fonctions globales exposées (`openAuthModal`, `openRegisterModal`, `openLoginModal`)
- ✅ Logs ASCII ajoutés pour le débogage
- ✅ CSS pour les suggestions d'adresse
- ✅ Validation : l'adresse doit être sélectionnée dans les suggestions

## 🧪 Tests à effectuer

### 1. Test du formulaire d'inscription

**URL**: https://mapevent.world

**Étapes**:
1. Cliquer sur "Connexion" dans le header
2. Cliquer sur "Créer un compte" dans le modal
3. Remplir le formulaire :
   - Prénom, Nom, Email, Username, Mot de passe
   - Photo de profil
4. **Test de l'adresse** :
   - Commencer à taper une adresse (ex: "Rue de la Paix, Genève")
   - Vérifier que des suggestions apparaissent après 3 caractères
   - Sélectionner une suggestion
   - Vérifier que le statut affiche "✓ Adresse vérifiée (CH)"
   - Cocher "Pas pour l'instant" pour tester le mode optionnel
5. Soumettre le formulaire

**Résultats attendus**:
- ✅ Les suggestions d'adresse s'affichent correctement
- ✅ La sélection d'une adresse remplit les champs cachés (lat, lng, country_code)
- ✅ Le statut affiche "✓ Adresse vérifiée"
- ✅ Si l'adresse n'est pas sélectionnée, un avertissement s'affiche
- ✅ L'inscription fonctionne avec ou sans adresse

### 2. Test de l'endpoint GET /api/user/me

**Commande PowerShell**:
```powershell
$LAMBDA_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
$TOKEN = "VOTRE_ACCESS_TOKEN"

Invoke-RestMethod -Uri "$LAMBDA_URL/api/user/me" -Method GET -Headers @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
}
```

**Résultats attendus**:
- ✅ La réponse contient un objet `address` avec :
  - `label`: L'adresse complète
  - `lat`: Latitude
  - `lng`: Longitude
  - `country_code`: Code pays (ex: "CH")
  - `city`: Ville
  - `postcode`: Code postal
  - `street`: Rue

### 3. Test de l'endpoint PUT /api/user/address

**Commande PowerShell**:
```powershell
$LAMBDA_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
$TOKEN = "VOTRE_ACCESS_TOKEN"

$body = @{
    label = "Rue de la Paix 1, 1204 Genève, Suisse"
    lat = 46.2044
    lng = 6.1432
    country_code = "CH"
    city = "Genève"
    postcode = "1204"
    street = "Rue de la Paix"
} | ConvertTo-Json

Invoke-RestMethod -Uri "$LAMBDA_URL/api/user/address" -Method PUT -Headers @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
} -Body $body
```

**Résultats attendus**:
- ✅ L'adresse est mise à jour avec succès
- ✅ La réponse contient l'adresse mise à jour
- ✅ Les coordonnées sont valides

### 4. Test de la console (logs ASCII)

**Dans la console du navigateur (F12)**:
```javascript
// Vérifier que les fonctions sont globales
typeof openAuthModal  // doit retourner "function"
typeof openRegisterModal  // doit retourner "function"
typeof openLoginModal  // doit retourner "function"

// Tester l'ouverture du modal
openAuthModal('register')

// Vérifier les logs
// Les logs doivent afficher :
// [AUTH] openAuthModal called with mode: register
// [AUTH] isRegister: true
```

**Résultats attendus**:
- ✅ Toutes les fonctions sont accessibles globalement
- ✅ Les logs ASCII s'affichent correctement
- ✅ Le modal s'ouvre en mode register

### 5. Test de l'autocomplete OpenStreetMap

**Dans le formulaire d'inscription**:
1. Taper "Rue de" dans le champ adresse
2. Attendre 300ms (debounce)
3. Vérifier que des suggestions apparaissent
4. Sélectionner une suggestion
5. Vérifier que les champs cachés sont remplis

**Résultats attendus**:
- ✅ Les suggestions apparaissent après 3 caractères
- ✅ Le debounce fonctionne (pas de requête à chaque frappe)
- ✅ La sélection remplit tous les champs nécessaires
- ✅ Le statut affiche "✓ Adresse vérifiée"

## 📝 Notes importantes

1. **OpenStreetMap/Nominatim** :
   - Service gratuit mais avec rate limiting
   - User-Agent requis : "MapEvent/1.0 (https://mapevent.world)"
   - Limite : 1 requête/seconde par IP

2. **Adresse optionnelle** :
   - L'utilisateur peut cocher "Pas pour l'instant"
   - Si une adresse est saisie, elle doit être vérifiée (sélectionnée)

3. **Validation** :
   - Les coordonnées sont validées (lat: -90 à 90, lng: -180 à 180)
   - Le country_code est requis si une adresse est fournie

4. **Alertes de proximité** :
   - La table `user_alert_settings` est prête pour les paramètres d'alertes
   - Les coordonnées stockées permettront de calculer les distances

## 🔍 Vérifications supplémentaires

### Vérifier la base de données
```sql
-- Vérifier les colonnes d'adresse
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name LIKE 'address%';

-- Vérifier la table user_alert_settings
SELECT * FROM user_alert_settings LIMIT 5;

-- Vérifier un utilisateur avec adresse
SELECT id, email, address_label, address_lat, address_lng, address_country_code 
FROM users 
WHERE address_label IS NOT NULL 
LIMIT 5;
```

## ✅ Checklist finale

- [x] Migration SQL exécutée
- [x] Backend déployé avec endpoints adresse
- [x] Frontend déployé avec composant adresse
- [ ] Test formulaire d'inscription (manuel)
- [ ] Test GET /api/user/me avec adresse
- [ ] Test PUT /api/user/address
- [ ] Test autocomplete OpenStreetMap
- [ ] Vérification logs console



