# ✅ Utiliser "test health" comme modèle - C'est OK !

## 🎯 Réponse rapide

**OUI, vous pouvez utiliser "test health" comme modèle !** ✅

Cela ne cassera **RIEN**. Vous allez juste créer un **nouvel événement** basé sur "test health".

## 📋 Étapes

### 1. Créer un nouvel événement

1. **Lambda** > Test
2. **"Configure test events"** ou menu déroulant
3. **"Create new event"** ou **"Créer un nouvel événement"**
4. Si on vous demande un **modèle**, choisissez **"test health"** ✅
5. C'est parfait, ça vous donne une structure de base

### 2. Modifier le JSON

Une fois que "test health" est chargé comme modèle, **modifiez juste** :

**Changez :**
```json
"path": "/api/health"
```
**En :**
```json
"path": "/api/admin/create-tables"
```

**Changez :**
```json
"httpMethod": "GET"
```
**En :**
```json
"httpMethod": "POST"
```

**Ajoutez :**
```json
"body": "{}"
```

### 3. Donner un nom

1. **Event name** : `create-tables`
2. **Sauvegardez**

### 4. Résultat final

Votre JSON devrait ressembler à :
```json
{
  "path": "/api/admin/create-tables",
  "httpMethod": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{}"
}
```

## ✅ Avantages

- ✅ Structure déjà correcte
- ✅ Headers déjà configurés
- ✅ Il suffit de changer le path et la méthode
- ✅ Plus rapide que de tout taper

## ⚠️ Important

- Vous créez un **NOUVEL événement** (pas de modification de "test health")
- "test health" reste intact
- Rien ne sera cassé

## 🎯 Action

1. **Créez un nouvel événement**
2. **Choisissez "test health" comme modèle** ✅
3. **Modifiez le path** : `/api/admin/create-tables`
4. **Modifiez la méthode** : `POST`
5. **Ajoutez** : `"body": "{}"`
6. **Nommez** : `create-tables`
7. **Sauvegardez**
8. **Testez**

C'est la méthode la plus simple ! Allez-y, ça ne cassera rien.

