# 🧪 Tests JWT - Endpoints d'authentification

## Prérequis

1. Variables d'environnement Lambda configurées :
   - `JWT_SECRET` : Secret pour signer les tokens (ex: `your-secret-key-here`)
   - `RDS_HOST`, `RDS_USER`, `RDS_PASSWORD`, etc.

2. Table `user_passwords` créée dans PostgreSQL (voir `database/schema.sql`)

## Tests PowerShell

### 1. Créer un utilisateur (register)

```powershell
$body = @{
    email = "test@example.com"
    password = "TestPassword123!"
    username = "testuser"
    firstName = "Test"
    lastName = "User"
    addresses = @(
        @{
            street = "Rue de Test 1"
            city = "Lausanne"
            zip = "1000"
            country = "CH"
            lat = 46.5197
            lng = 6.6323
        }
    )
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api/user/register" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body
```

### 2. Se connecter (login) - Obtient accessToken + refreshToken

```powershell
$body = @{
    email = "test@example.com"
    password = "TestPassword123!"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api/auth/login" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body

$data = $response.Content | ConvertFrom-Json
$accessToken = $data.accessToken
$refreshToken = $data.refreshToken

Write-Host "Access Token: $($accessToken.Substring(0, 50))..."
Write-Host "Refresh Token: $($refreshToken.Substring(0, 50))..."
```

### 3. Récupérer le profil (GET /api/user/me)

```powershell
$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $accessToken"
}

$response = Invoke-WebRequest -Uri "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api/user/me" `
    -Method GET `
    -Headers $headers

$data = $response.Content | ConvertFrom-Json
Write-Host "User: $($data.user.email)"
Write-Host "Role: $($data.user.role)"
Write-Host "Subscription: $($data.user.subscription)"
```

### 4. Rafraîchir le token (POST /api/auth/refresh)

```powershell
$body = @{
    refreshToken = $refreshToken
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api/auth/refresh" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body

$data = $response.Content | ConvertFrom-Json
$newAccessToken = $data.accessToken
Write-Host "New Access Token: $($newAccessToken.Substring(0, 50))..."
```

### 5. Test avec token invalide (doit retourner 401)

```powershell
$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer invalid-token-here"
}

try {
    Invoke-WebRequest -Uri "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api/user/me" `
        -Method GET `
        -Headers $headers
} catch {
    Write-Host "Erreur attendue (401): $($_.Exception.Response.StatusCode)"
}
```

## Tests cURL (alternative)

### 1. Login

```bash
curl -X POST https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPassword123!"}'
```

### 2. GET /api/user/me

```bash
curl -X GET https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api/user/me \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### 3. Refresh

```bash
curl -X POST https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refreshToken":"YOUR_REFRESH_TOKEN_HERE"}'
```

## Vérifications

- ✅ `/api/auth/login` retourne `accessToken`, `refreshToken`, `user`
- ✅ `/api/user/me` retourne le profil complet depuis PostgreSQL
- ✅ `/api/user/me` rejette les requêtes sans token (401)
- ✅ `/api/user/me` rejette les tokens invalides (401)
- ✅ `/api/auth/refresh` génère un nouvel `accessToken`
- ✅ Le frontend charge l'utilisateur depuis `/api/user/me` au démarrage




