# 🔧 Maintenance avec create-tables

## ✅ Méthode de maintenance (30 secondes)

### Pour recréer les tables

1. **Lambda** > Fonction `mapevent-backend`
2. Onglet **"Test"**
3. Menu déroulant : Sélectionnez **"create-tables"** (que vous avez déjà créé)
4. Cliquez sur **"Test"** (bouton orange)
5. Attendez 5 secondes
6. ✅ **Les tables sont recréées !**

### Vérification

Vous verrez :
```json
{
  "statusCode": 200,
  "body": "{\"status\":\"success\",\"message\":\"Tables créées avec succès\",\"tables\":[...]}"
}
```

## 📋 Quand faire la maintenance

### Scénarios où recréer les tables

1. **Vous avez supprimé des tables** par erreur
2. **Vous voulez réinitialiser** la base de données
3. **Problème de structure** des tables
4. **Migration** vers une nouvelle structure
5. **Test** d'une nouvelle base de données

## ⚠️ Attention

### Avant de recréer les tables

⚠️ **Recréer les tables EFFACE toutes les données existantes !**

- ✅ Les tables seront recréées vides
- ❌ Toutes les données seront perdues
- ⚠️ Faites une sauvegarde avant si vous avez des données importantes

## 🔄 Processus de maintenance complet

### 1. Sauvegarder les données (si nécessaire)

Si vous avez des données importantes :
- Exportez-les depuis votre base de données
- Ou faites un backup RDS

### 2. Recréer les tables

1. Lambda > Test > "create-tables" > Test
2. Attendez 5 secondes
3. ✅ Tables recréées

### 3. Restaurer les données (si nécessaire)

Si vous aviez exporté des données :
- Réimportez-les dans les nouvelles tables

## ✅ Avantages de cette méthode

- ✅ **Rapide** : 30 secondes
- ✅ **Simple** : Juste Lambda > Test
- ✅ **Fiable** : Fonctionne toujours (même si API Gateway a des problèmes)
- ✅ **Pas besoin d'API Gateway** : Directement via Lambda

## 🎯 Résumé

**Pour la maintenance :**
1. Lambda > Test
2. Sélectionner "create-tables"
3. Cliquer "Test"
4. C'est fait !

**C'est simple, rapide, et ça fonctionne toujours !**

