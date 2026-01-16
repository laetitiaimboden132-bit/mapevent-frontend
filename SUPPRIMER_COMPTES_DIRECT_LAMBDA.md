# ✅ SOLUTION SIMPLE : Utiliser Lambda directement (sans API Gateway)

## 🎯 Problème

Les endpoints ne sont pas accessibles via API Gateway (403). **Mais Lambda fonctionne !**

## ✅ Solution : Appeler Lambda directement via AWS CLI

Puisque Lambda est dans le même VPC que RDS, on peut invoquer Lambda directement.

---

## 📋 ÉTAPES SIMPLES

### Étape 1 : Voir tous vos comptes

**Créez un fichier `list-users-payload.json` :**

```json
{
  "httpMethod": "GET",
  "path": "/api/admin/list-users",
  "headers": {},
  "queryStringParameters": null,
  "body": null
}
```

**Puis exécutez :**

```powershell
aws lambda invoke `
  --function-name mapevent-backend `
  --region eu-west-1 `
  --payload file://list-users-payload.json `
  --cli-binary-format raw-in-base64-out `
  response.json

Get-Content response.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

---

### Étape 2 : Supprimer tous sauf un compte

**Créez un fichier `delete-except-payload.json` :**

```json
{
  "httpMethod": "POST",
  "path": "/api/admin/delete-all-users-except",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"keepEmail\": \"VOTRE-EMAIL-ADMIN@example.com\"}"
}
```

**⚠️ REMPLACEZ `VOTRE-EMAIL-ADMIN@example.com` par l'email de votre compte admin !**

**Puis exécutez :**

```powershell
aws lambda invoke `
  --function-name mapevent-backend `
  --region eu-west-1 `
  --payload file://delete-except-payload.json `
  --cli-binary-format raw-in-base64-out `
  response.json

Get-Content response.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

---

## 🚀 Script PowerShell automatique

J'ai créé `supprimer-comptes-direct-lambda.ps1` qui fait tout automatiquement !

**Exécutez simplement :**

```powershell
cd C:\MapEventAI_NEW\frontend
.\supprimer-comptes-direct-lambda.ps1
```

---

## ✅ Avantages

- ✅ **Lambda est dans le même VPC** → Accès direct à RDS
- ✅ **Pas besoin d'API Gateway** → Pas de problème de configuration
- ✅ **AWS CLI déjà installé** → Pas d'installation supplémentaire
- ✅ **Simple et rapide** → Une seule commande

---

## 🆘 Si AWS CLI n'est pas installé

**Installez AWS CLI :**

1. Téléchargez : https://aws.amazon.com/cli/
2. Installez
3. Configurez : `aws configure`
   - Access Key ID : Votre clé AWS
   - Secret Access Key : Votre clé secrète
   - Region : `eu-west-1`
   - Output format : `json`

