# 🗺️ Navigation dans S3 - Guide étape par étape

## 📍 Où aller exactement

### ❌ NE PAS cliquer sur "avatars/"

**Ne cliquez PAS sur l'objet "avatars/"** - C'est juste un dossier avec vos images.

### ✅ Cliquez sur le NOM du bucket

**Cliquez sur le NOM du bucket** `mapevent-avatars` (pas sur la case à cocher, mais sur le nom lui-même).

---

## 🎯 Étapes détaillées

### Étape 1 : Ouvrir la console S3

1. **Allez sur** : https://console.aws.amazon.com/s3/
2. **Connectez-vous** avec vos identifiants AWS

### Étape 2 : Trouver votre bucket

1. Vous verrez une **liste de buckets** (compartiments)
2. **Cherchez** : `mapevent-avatars`
3. **Cliquez sur le NOM** `mapevent-avatars` (pas sur la case à cocher à gauche)

### Étape 3 : Vous êtes maintenant dans le bucket

Une fois que vous avez cliqué sur le nom du bucket, vous verrez :

- **En haut** : Des **onglets** :
  - Objets
  - Propriétés
  - **Autorisations** ← **C'EST ICI QU'IL FAUT ALLER !**
  - Métriques
  - etc.

- **En dessous** : La liste des objets (dossiers et fichiers)
  - Vous verrez `avatars/` dans la liste
  - **NE CLIQUEZ PAS dessus** pour configurer CORS/Policy

### Étape 4 : Aller dans Autorisations

1. **Cliquez sur l'onglet "Autorisations"** (en haut de la page)
2. Vous verrez plusieurs sections :
   - Blocage de l'accès public (bucket settings)
   - **Politique du compartiment** ← **C'EST ICI !**
   - Partage de ressources cross-origin (CORS) ← **ET ICI !**
   - Liste de contrôle d'accès (ACL) ← **IGNOREZ CELUI-CI**

---

## 📋 Résumé visuel

```
Console S3
  └── Liste des buckets
      └── [ ] mapevent-avatars  ← CLIQUEZ SUR LE NOM (pas la case)
          │
          ├── Onglet "Objets" (liste des fichiers)
          ├── Onglet "Propriétés"
          ├── Onglet "Autorisations" ← ALLEZ ICI !
          │   ├── Blocage de l'accès public
          │   ├── Politique du compartiment ← CONFIGUREZ ICI
          │   ├── Partage de ressources cross-origin (CORS) ← CONFIGUREZ ICI
          │   └── Liste de contrôle d'accès (ACL) ← IGNOREZ
          └── Onglet "Métriques"
```

---

## ✅ Ce qu'il faut faire

1. **Cliquez sur le nom du bucket** `mapevent-avatars`
2. **Cliquez sur l'onglet "Autorisations"** (en haut)
3. **Configurez "Politique du compartiment"** (cliquez sur "Modifier")
4. **Configurez "Partage de ressources cross-origin (CORS)"** (cliquez sur "Modifier")

**C'est tout !** Vous n'avez pas besoin de cliquer sur "avatars/" ou sur les fichiers.

---

## 🆘 Si vous êtes perdu

### Vous êtes au bon endroit si vous voyez :

- ✅ Des **onglets en haut** : Objets, Propriétés, Autorisations, etc.
- ✅ La section **"Politique du compartiment"**
- ✅ La section **"Partage de ressources cross-origin (CORS)"**

### Vous êtes au mauvais endroit si vous voyez :

- ❌ Juste une liste de fichiers (avatars/, etc.)
- ❌ Les détails d'un fichier spécifique
- ❌ Pas d'onglets en haut

**Si vous êtes au mauvais endroit** :
- Cliquez sur "mapevent-avatars" dans le fil d'Ariane (breadcrumb) en haut
- Ou retournez à la liste des buckets et recliquez sur le nom du bucket

---

Dites-moi si vous voyez bien l'onglet "Autorisations" maintenant ! 😊




