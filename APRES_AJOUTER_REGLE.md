# ✅ APRÈS AVOIR AJOUTÉ LA RÈGLE - QUE FAIRE ?

## 🎯 ÉTAPES SUIVANTES

### 1. ✅ Vérifier que la règle est bien enregistrée

1. **Dans AWS**, vous devriez voir votre nouvelle règle dans la liste
2. Elle devrait apparaître comme :
   - **Type** : PostgreSQL
   - **Source** : Votre IP/32 (exemple : `81.13.194.194/32`)
   - **Port** : 5432

**Si vous la voyez, c'est bon !** ✅

---

### 2. ⏳ Attendre 1-2 minutes

**Important :** Attendez 1-2 minutes que la règle soit appliquée.

---

### 3. 🚀 Exécuter le script Python

**Ouvrez PowerShell** dans le dossier du projet et exécutez :

```powershell
python supprimer-comptes.py
```

---

### 4. 📋 Ce qui va se passer

Le script va :
1. ✅ Se connecter à votre base de données
2. ✅ Vous montrer **tous vos comptes** avec leur email et rôle
3. ✅ Vous demander **quel compte garder**
4. ✅ Supprimer tous les autres automatiquement

---

## 🎯 EXEMPLE CONCRET

**Quand vous exécutez le script, vous verrez :**

```
============================================================
SUPPRESSION DES COMPTES - METHODE ULTRA-SIMPLE
============================================================

Connexion a la base de donnees...
  OK: Connecte!

ETAPE 1: Liste de tous les comptes...

Nombre de comptes trouves: 3

LISTE DES COMPTES:
  - admin@mapevent.world (director)
    Nom: Admin User
  - test@example.com
    Nom: Test User
  - autre@example.com
    Nom: Autre User

Quel compte voulez-vous GARDER?
  (Tapez l'email du compte a garder)
  (Ou laissez vide pour supprimer TOUS les comptes)

Email du compte a garder (ou Entree pour tout supprimer): 
```

**Vous tapez l'email du compte à garder, par exemple :**
```
admin@mapevent.world
```

**Le script supprime tous les autres automatiquement !**

---

## ✅ RÉSUMÉ

1. ✅ **Règle ajoutée** dans AWS (vous l'avez fait)
2. ⏳ **Attendre 1-2 minutes**
3. 🚀 **Exécuter** : `python supprimer-comptes.py`
4. 📋 **Voir vos comptes** et choisir lequel garder
5. ✅ **C'est tout !**

---

**Attendez 1-2 minutes, puis exécutez le script Python !** 🚀


