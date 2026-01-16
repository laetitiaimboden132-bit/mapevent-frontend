# 🔐 Configuration JWT_SECRET dans AWS Lambda

## Étapes pour configurer JWT_SECRET

### 1. Générer un secret aléatoire

**Option A : PowerShell (Windows)**
```powershell
# Générer 32 bytes (64 caractères hex)
$bytes = New-Object byte[] 32
[System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
$secret = [System.BitConverter]::ToString($bytes).Replace("-", "").ToLower()
Write-Host "JWT_SECRET=$secret"
```

**Option B : OpenSSL (si installé)**
```bash
openssl rand -hex 32
```

**Option C : Python**
```python
import secrets
print(secrets.token_hex(32))
```

### 2. Ajouter dans AWS Lambda Console

1. Aller dans **AWS Console** → **Lambda**
2. Sélectionner la fonction **`mapevent-backend`**
3. Aller dans **Configuration** → **Variables d'environnement**
4. Cliquer sur **Modifier**
5. Cliquer sur **Ajouter une variable d'environnement**
6. **Clé** : `JWT_SECRET`
7. **Valeur** : Coller le secret généré (ex: `a1b2c3d4e5f6...`)
8. Cliquer sur **Enregistrer**

### 3. Vérifier la configuration

```powershell
aws lambda get-function-configuration `
  --function-name mapevent-backend `
  --region eu-west-1 `
  --query 'Environment.Variables.JWT_SECRET' `
  --output text
```

### 4. Alternative : Configuration via AWS CLI

```powershell
# Récupérer les variables actuelles
$currentEnv = aws lambda get-function-configuration `
  --function-name mapevent-backend `
  --region eu-west-1 `
  --query 'Environment.Variables' `
  --output json | ConvertFrom-Json

# Ajouter JWT_SECRET
$currentEnv | Add-Member -MemberType NoteProperty -Name "JWT_SECRET" -Value "VOTRE_SECRET_ICI" -Force

# Convertir en format AWS CLI
$envJson = $currentEnv | ConvertTo-Json -Compress

# Mettre à jour
aws lambda update-function-configuration `
  --function-name mapevent-backend `
  --region eu-west-1 `
  --environment "Variables=$envJson"
```

## ⚠️ Sécurité

- **NE JAMAIS** commiter `JWT_SECRET` dans Git
- Utiliser un secret différent pour chaque environnement (dev, staging, prod)
- Régénérer le secret si compromis
- Longueur recommandée : 64 caractères (32 bytes en hex)

## 🔄 Après configuration

1. Redémarrer la fonction Lambda (ou attendre quelques secondes)
2. Tester avec `test_jwt.ps1`
3. Vérifier les logs CloudWatch si erreur




