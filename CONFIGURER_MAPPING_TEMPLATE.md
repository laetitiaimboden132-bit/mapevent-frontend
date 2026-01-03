# 🔧 Configuration du Mapping Template dans API Gateway

## ✅ Réponse rapide

Pour une **intégration Lambda Proxy**, sélectionnez :

**"Lorsqu'aucun modèle n'est défini"** ou **"Jamais"**

## 📋 Explication détaillée

### Si vous utilisez "Use Lambda Proxy integration" (recommandé)

Quand vous cochez **"Use Lambda Proxy integration"**, vous n'avez **PAS BESOIN** de mapping templates.

Dans ce cas :
- Sélectionnez **"Jamais"** ou **"Lorsqu'aucun modèle n'est défini"**
- Laissez les champs de mapping template **vides**
- Lambda recevra directement l'événement complet

### Si vous n'utilisez PAS Lambda Proxy integration

Alors vous devez configurer les mapping templates :
- **Request body passthrough** : "Lorsqu'aucun modèle ne correspond au type de contenu"
- Créez un mapping template pour transformer la requête

## ✅ Configuration recommandée

### Pour `/api/admin/create-tables` :

1. **Use Lambda Proxy integration** : ✅ **COCHÉ**
2. **Request body passthrough** : **"Jamais"** ou **"Lorsqu'aucun modèle n'est défini"**
3. **Mapping templates** : **LAISSER VIDES**

### Pourquoi ?

Avec Lambda Proxy :
- Lambda reçoit l'événement complet tel quel
- Pas besoin de transformation
- Plus simple et plus flexible

## 🔍 Où trouver cette option ?

1. **Integration Request**
2. Section **"Mapping Templates"**
3. **Request body passthrough** : 
   - Dropdown avec les options :
     - "Lorsqu'aucun modèle n'est défini"
     - "Lorsqu'aucun modèle ne correspond au type de contenu"
     - "Jamais"

## ✅ Action à faire

**Sélectionnez "Jamais"** ou **"Lorsqu'aucun modèle n'est défini"**

Les deux fonctionnent si vous utilisez Lambda Proxy integration.

## ⚠️ Important

Si vous voyez cette option, c'est que vous êtes dans la section **Mapping Templates**.

**Assurez-vous que :**
- ✅ "Use Lambda Proxy integration" est **COCHÉ**
- ✅ Les mapping templates sont **VIDES**
- ✅ Request body passthrough : **"Jamais"** ou **"Lorsqu'aucun modèle n'est défini"**

## 🎯 Résumé

**Pour votre route `/api/admin/create-tables` :**

```
Integration type: Lambda Function
Use Lambda Proxy integration: ✓ (COCHÉ)
Request body passthrough: "Jamais" (ou "Lorsqu'aucun modèle n'est défini")
Mapping templates: VIDES
```

C'est tout ! Pas besoin de configurer de mapping template avec Lambda Proxy.

