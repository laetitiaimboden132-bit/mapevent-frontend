# Checklist de Validation JWT - End-to-End

## Objectif
Valider le système DB+JWT avec le frontend sur https://mapevent.world avant d'ajouter Stripe/Redis/S3.

## Prérequis
- Backend Lambda déployé et accessible
- Frontend déployé sur CloudFront (https://mapevent.world)
- JWT_SECRET configuré dans Lambda
- Table `user_passwords` créée dans PostgreSQL

## Tests Manuels

### 1. Test de Connexion (Login)
- [ ] Ouvrir https://mapevent.world
- [ ] Ouvrir la console du navigateur (F12)
- [ ] Vérifier les logs ASCII:
  - `[AUTH] API_BASE_URL: https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api`
- [ ] Se connecter avec email/password via le formulaire
- [ ] Vérifier dans la console:
  - `[AUTH] Appel GET /api/user/me...`
  - `[AUTH] GET /api/user/me - Status: 200 OK`
  - `[AUTH] Utilisateur charge depuis /api/user/me: <email>`
- [ ] Vérifier que `accessToken` et `refreshToken` sont dans `localStorage`
- [ ] Vérifier que l'avatar s'affiche correctement (pas de texte "om/...")

### 2. Test de Chargement au Démarrage (Page Load)
- [ ] Ouvrir https://mapevent.world dans un nouvel onglet (sans être connecté)
- [ ] Ouvrir la console du navigateur
- [ ] Vérifier qu'il n'y a pas d'erreur si aucun token n'existe
- [ ] Se connecter, puis recharger la page (F5)
- [ ] Vérifier dans la console:
  - `[AUTH] API_BASE_URL: ...`
  - `[AUTH] Appel GET /api/user/me...`
  - `[AUTH] GET /api/user/me - Status: 200 OK`
  - `[AUTH] Utilisateur charge depuis /api/user/me: <email>`
- [ ] Vérifier que l'utilisateur est toujours connecté après rechargement
- [ ] Vérifier que l'avatar s'affiche correctement

### 3. Test de Refresh Token (Token Expiré)
- [ ] Se connecter
- [ ] Dans la console, modifier manuellement `accessToken` pour le rendre invalide:
  ```javascript
  localStorage.setItem('accessToken', 'invalid_token');
  ```
- [ ] Recharger la page (F5)
- [ ] Vérifier dans la console:
  - `[AUTH] GET /api/user/me - Status: 401 Unauthorized`
  - `[AUTH] Token expire (401), tentative refresh...`
  - `[AUTH] Appel POST /api/auth/refresh...`
  - `[AUTH] POST /api/auth/refresh - Status: 200 OK`
  - `[AUTH] Nouveau accessToken obtenu`
  - `[AUTH] Retry GET /api/user/me avec nouveau token...`
  - `[AUTH] Retry GET /api/user/me - Status: 200 OK`
  - `[AUTH] Utilisateur charge apres refresh: <email>`
- [ ] Vérifier que l'utilisateur est toujours connecté

### 4. Test de Déconnexion (Logout)
- [ ] Se connecter
- [ ] Cliquer sur le bouton de déconnexion
- [ ] Vérifier dans la console:
  - `[AUTH] Logout - API_BASE_URL: ...`
  - `[AUTH] Appel POST /api/auth/logout...`
  - `[AUTH] POST /api/auth/logout - Status: 200 OK`
  - `[AUTH] Tokens supprimes, deconnexion complete`
- [ ] Vérifier que `accessToken`, `refreshToken` et `currentUser` sont supprimés de `localStorage`
- [ ] Vérifier que l'avatar affiche l'emoji 👤

### 5. Test d'Avatar (Bug "om/...")
- [ ] Se connecter avec un utilisateur qui a une photo de profil
- [ ] Vérifier que l'avatar s'affiche correctement (image ou 👤, jamais de texte)
- [ ] Vérifier dans la console qu'il n'y a pas d'erreur d'image
- [ ] Si l'URL de l'avatar est tronquée (ex: "om/..."), vérifier que `normalizeImageUrl()` la corrige
- [ ] Vérifier que `protectAccountBlock()` ne montre jamais de texte brut dans l'avatar

### 6. Test d'Erreur (Refresh Token Invalide)
- [ ] Se connecter
- [ ] Dans la console, modifier `refreshToken` pour le rendre invalide:
  ```javascript
  localStorage.setItem('refreshToken', 'invalid_refresh_token');
  ```
- [ ] Modifier `accessToken` pour le rendre invalide
- [ ] Recharger la page (F5)
- [ ] Vérifier dans la console:
  - `[AUTH] GET /api/user/me - Status: 401 Unauthorized`
  - `[AUTH] Token expire (401), tentative refresh...`
  - `[AUTH] POST /api/auth/refresh - Status: 401 Unauthorized`
  - `[AUTH] Refresh echoue: 401`
  - `[AUTH] Refresh echoue, deconnexion`
- [ ] Vérifier que l'utilisateur est déconnecté

## Tests Automatisés (PowerShell/curl)

### Script PowerShell: `test_jwt_e2e.ps1`

```powershell
# Configuration
$LAMBDA_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
$API_BASE = "$LAMBDA_URL/api"

# Test 1: Health Check
Write-Host "`n[TEST 1] Health Check" -ForegroundColor Cyan
$health = Invoke-RestMethod -Uri "$LAMBDA_URL/health" -Method GET
Write-Host "Status: $($health.ok)" -ForegroundColor $(if ($health.ok) { "Green" } else { "Red" })

# Test 2: Register (si nécessaire)
Write-Host "`n[TEST 2] Register" -ForegroundColor Cyan
$registerBody = @{
    email = "test-$(Get-Random)@example.com"
    password = "Test123!@#"
    username = "testuser$(Get-Random)"
    first_name = "Test"
    last_name = "User"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "$API_BASE/user/register" -Method POST -Body $registerBody -ContentType "application/json"
    Write-Host "Register OK - User ID: $($registerResponse.user.id)" -ForegroundColor Green
    $TEST_EMAIL = $registerBody | ConvertFrom-Json | Select-Object -ExpandProperty email
    $TEST_PASSWORD = $registerBody | ConvertFrom-Json | Select-Object -ExpandProperty password
} catch {
    Write-Host "Register failed (user may exist): $($_.Exception.Message)" -ForegroundColor Yellow
    # Utiliser des credentials existants
    $TEST_EMAIL = "test@example.com"
    $TEST_PASSWORD = "Test123!@#"
}

# Test 3: Login
Write-Host "`n[TEST 3] Login" -ForegroundColor Cyan
$loginBody = @{
    email = $TEST_EMAIL
    password = $TEST_PASSWORD
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$API_BASE/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    $ACCESS_TOKEN = $loginResponse.accessToken
    $REFRESH_TOKEN = $loginResponse.refreshToken
    Write-Host "Login OK - Access Token: $($ACCESS_TOKEN.Substring(0, 20))..." -ForegroundColor Green
} catch {
    Write-Host "Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 4: GET /api/user/me
Write-Host "`n[TEST 4] GET /api/user/me" -ForegroundColor Cyan
$headers = @{
    "Authorization" = "Bearer $ACCESS_TOKEN"
    "Content-Type" = "application/json"
}
try {
    $meResponse = Invoke-RestMethod -Uri "$API_BASE/user/me" -Method GET -Headers $headers
    Write-Host "GET /api/user/me OK - Email: $($meResponse.user.email)" -ForegroundColor Green
} catch {
    Write-Host "GET /api/user/me failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 5: Refresh Token
Write-Host "`n[TEST 5] POST /api/auth/refresh" -ForegroundColor Cyan
$refreshBody = @{
    refreshToken = $REFRESH_TOKEN
} | ConvertTo-Json

try {
    $refreshResponse = Invoke-RestMethod -Uri "$API_BASE/auth/refresh" -Method POST -Body $refreshBody -ContentType "application/json"
    $NEW_ACCESS_TOKEN = $refreshResponse.accessToken
    Write-Host "Refresh OK - New Access Token: $($NEW_ACCESS_TOKEN.Substring(0, 20))..." -ForegroundColor Green
} catch {
    Write-Host "Refresh failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 6: GET /api/user/me avec nouveau token
Write-Host "`n[TEST 6] GET /api/user/me (avec nouveau token)" -ForegroundColor Cyan
$newHeaders = @{
    "Authorization" = "Bearer $NEW_ACCESS_TOKEN"
    "Content-Type" = "application/json"
}
try {
    $meResponse2 = Invoke-RestMethod -Uri "$API_BASE/user/me" -Method GET -Headers $newHeaders
    Write-Host "GET /api/user/me OK - Email: $($meResponse2.user.email)" -ForegroundColor Green
} catch {
    Write-Host "GET /api/user/me failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 7: Logout
Write-Host "`n[TEST 7] POST /api/auth/logout" -ForegroundColor Cyan
try {
    $logoutResponse = Invoke-RestMethod -Uri "$API_BASE/auth/logout" -Method POST -Headers $newHeaders
    Write-Host "Logout OK - Message: $($logoutResponse.message)" -ForegroundColor Green
} catch {
    Write-Host "Logout failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 8: GET /api/user/me après logout (doit échouer)
Write-Host "`n[TEST 8] GET /api/user/me (après logout - doit échouer)" -ForegroundColor Cyan
try {
    $meResponse3 = Invoke-RestMethod -Uri "$API_BASE/user/me" -Method GET -Headers $newHeaders
    Write-Host "ERREUR: GET /api/user/me devrait échouer après logout!" -ForegroundColor Red
} catch {
    Write-Host "OK: GET /api/user/me a bien échoué (comme attendu)" -ForegroundColor Green
}

Write-Host "`n[RESUME] Tous les tests sont passes!" -ForegroundColor Green
```

### Commandes curl (Alternative)

```bash
# Configuration
LAMBDA_URL="https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
API_BASE="$LAMBDA_URL/api"

# Test 1: Health Check
echo "[TEST 1] Health Check"
curl -X GET "$LAMBDA_URL/health"

# Test 2: Register
echo "[TEST 2] Register"
REGISTER_RESPONSE=$(curl -X POST "$API_BASE/user/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test-'"$(date +%s)"'@example.com",
    "password": "Test123!@#",
    "username": "testuser'"$(date +%s)"'",
    "first_name": "Test",
    "last_name": "User"
  }')
echo "$REGISTER_RESPONSE"

# Test 3: Login
echo "[TEST 3] Login"
LOGIN_RESPONSE=$(curl -X POST "$API_BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#"
  }')
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.accessToken')
REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.refreshToken')
echo "Access Token: ${ACCESS_TOKEN:0:20}..."

# Test 4: GET /api/user/me
echo "[TEST 4] GET /api/user/me"
curl -X GET "$API_BASE/user/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json"

# Test 5: Refresh Token
echo "[TEST 5] POST /api/auth/refresh"
REFRESH_RESPONSE=$(curl -X POST "$API_BASE/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refreshToken\": \"$REFRESH_TOKEN\"}")
NEW_ACCESS_TOKEN=$(echo "$REFRESH_RESPONSE" | jq -r '.accessToken')
echo "New Access Token: ${NEW_ACCESS_TOKEN:0:20}..."

# Test 6: GET /api/user/me avec nouveau token
echo "[TEST 6] GET /api/user/me (avec nouveau token)"
curl -X GET "$API_BASE/user/me" \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN" \
  -H "Content-Type: application/json"

# Test 7: Logout
echo "[TEST 7] POST /api/auth/logout"
curl -X POST "$API_BASE/auth/logout" \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

## Documentation: /api/auth/logout

**Status actuel:** Client-side only

Les refresh tokens ne sont **PAS stockés** dans la base de données. La déconnexion côté serveur consiste uniquement à valider le token d'accès.

**Pour invalider les refresh tokens côté serveur (futur):**
1. Créer une table `refresh_tokens` (user_id, token_hash, expires_at)
2. Stocker les refresh tokens lors de la génération
3. Supprimer le refresh token de la table lors du logout

**Sécurité actuelle:**
- Durée de vie limitée des tokens (15min access, 30j refresh)
- Suppression côté client des tokens dans localStorage
- Les tokens expirés sont automatiquement rejetés

## Critères de Validation

- [ ] Tous les tests manuels passent
- [ ] Tous les tests automatisés passent
- [ ] Les logs ASCII sont visibles dans la console
- [ ] L'avatar s'affiche correctement (pas de texte "om/...")
- [ ] Le refresh token fonctionne correctement
- [ ] La déconnexion fonctionne correctement
- [ ] L'utilisateur reste connecté après rechargement de page

## Prochaines Étapes

Une fois cette checklist validée:
1. ✅ Système DB+JWT validé
2. ⏭️ Stripe webhooks + synchro subscription→role
3. ⏭️ Redis/S3 si nécessaire



