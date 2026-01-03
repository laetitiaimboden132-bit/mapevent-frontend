# 🔒 Sécurité RDS - Risques et Solutions

## ⚠️ RISQUES si quelqu'un possède le mot de passe RDS

### Risques Critiques :
1. **Accès complet à la base de données**
   - Lecture de TOUTES les données (utilisateurs, événements, messages privés)
   - Modification/suppression de données
   - Vol d'informations personnelles (emails, adresses)

2. **Corruption de données**
   - Suppression de tables entières
   - Modification malveillante des données
   - Injection SQL

3. **Coûts AWS**
   - Création de ressources coûteuses
   - Export de données volumineuses

4. **Violation RGPD**
   - Accès non autorisé aux données personnelles
   - Risques légaux et amendes

## 🛡️ SOLUTIONS IMMÉDIATES

### 1. Restreindre l'accès via Security Groups (CRITIQUE)

Votre RDS doit être accessible **UNIQUEMENT** depuis :
- Votre Lambda function
- Votre IP personnelle (pour administration)

**Vérifier les Security Groups :**
```powershell
aws rds describe-db-instances --db-instance-identifier mapevent-db --region eu-west-1 --query 'DBInstances[0].VpcSecurityGroups'
```

**Restreindre l'accès :**
- Dans AWS Console > RDS > mapevent-db > Connectivity & security
- Vérifiez que le Security Group autorise SEULEMENT :
  - Port 5432 depuis votre VPC Lambda
  - Port 5432 depuis votre IP (pour administration)

### 2. Changer le mot de passe immédiatement

Si vous suspectez une fuite, changez-le maintenant :
```powershell
.\reset_rds_password.ps1
```

### 3. Activer la surveillance (CloudTrail)

Surveillez les accès suspects :
```powershell
aws cloudtrail lookup-events --lookup-attributes AttributeKey=ResourceName,AttributeValue=mapevent-db --region eu-west-1
```

### 4. Utiliser AWS Secrets Manager (RECOMMANDÉ)

Au lieu de stocker le mot de passe en clair dans `lambda.env`, utilisez Secrets Manager :

**Créer un secret :**
```powershell
aws secretsmanager create-secret --name mapevent/rds/password --secret-string "mwh3!Cq&vB$s1*Zx" --region eu-west-1
```

**Lambda récupère automatiquement le secret** (plus besoin de lambda.env)

## 🔐 BONNES PRATIQUES

### ✅ À FAIRE :
- ✅ Utiliser AWS Secrets Manager pour les mots de passe
- ✅ Restreindre les Security Groups au strict minimum
- ✅ Activer le chiffrement RDS (déjà activé ✅)
- ✅ Activer les backups automatiques (déjà activé ✅)
- ✅ Utiliser IAM Database Authentication (optionnel)
- ✅ Surveiller les accès via CloudTrail
- ✅ Rotation automatique des mots de passe (Secrets Manager)

### ❌ À NE JAMAIS FAIRE :
- ❌ Commiter les mots de passe dans Git
- ❌ Partager les mots de passe en clair (email, chat, etc.)
- ❌ Laisser RDS accessible depuis Internet (0.0.0.0/0)
- ❌ Utiliser le même mot de passe partout
- ❌ Stocker les mots de passe dans le code

## 🚨 ACTIONS IMMÉDIATES RECOMMANDÉES

1. **Vérifier les Security Groups** (5 min)
2. **Changer le mot de passe** si suspect de fuite (2 min)
3. **Migrer vers Secrets Manager** (10 min)
4. **Activer CloudTrail** pour surveillance (5 min)

## 📊 VÉRIFICATION DE SÉCURITÉ

Exécutez ce script pour vérifier votre configuration :

```powershell
# Vérifier que RDS n'est pas public
aws rds describe-db-instances --db-instance-identifier mapevent-db --region eu-west-1 --query 'DBInstances[0].PubliclyAccessible'

# Doit retourner: false

# Vérifier les Security Groups
aws rds describe-db-instances --db-instance-identifier mapevent-db --region eu-west-1 --query 'DBInstances[0].VpcSecurityGroups[*].VpcSecurityGroupId'
```





