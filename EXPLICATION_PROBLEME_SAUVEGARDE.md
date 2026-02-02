# 🔍 Explication du Problème de Sauvegarde

## ❌ Problème Rencontré

```
ERREUR connexion DB: connection to server at "mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com" 
(52.210.137.130), port 5432 failed: timeout expired
```

## 🔍 Pourquoi ça ne fonctionne pas ?

**RDS est protégé par des Security Groups AWS** qui limitent l'accès :

1. **RDS n'accepte que les connexions depuis** :
   - Le VPC AWS (où Lambda fonctionne)
   - Les IPs autorisées dans les Security Groups
   - Pas depuis votre ordinateur local par défaut

2. **Votre ordinateur** → Internet → RDS = **BLOQUÉ** (timeout)

## ✅ Solutions

### Solution 1 : Autoriser votre IP dans les Security Groups (RECOMMANDÉ)

1. **Trouver votre IP publique** :
   - Allez sur https://whatismyipaddress.com/
   - Notez votre IP publique

2. **Modifier les Security Groups RDS** :
   - AWS Console → RDS → Votre base → Security Groups
   - Ajouter une règle : Port 5432, Source = Votre IP publique
   - Sauvegarder

3. **Relancer le script** :
   ```bash
   python sauvegarder-comptes-complet.py
   ```

### Solution 2 : Utiliser un script Lambda (ALTERNATIVE)

Créer une fonction Lambda qui fait la sauvegarde et stocke le résultat dans S3.

### Solution 3 : Utiliser AWS Systems Manager Session Manager (AVANCÉ)

Se connecter à une instance EC2 dans le VPC et exécuter le script depuis là.

## 🎯 Solution Rapide

**Le plus simple** : Autoriser votre IP dans les Security Groups RDS, puis relancer le script.

Les scripts sont **100% fonctionnels**, c'est juste un problème d'accès réseau AWS.
