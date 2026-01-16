# 🚀 INSTRUCTIONS FINALES - SUPPRIMER TOUS LES COMPTES

## ⚠️ L'ENDPOINT API A UN PROBLÈME (ERREUR 500)

**L'erreur 500 indique que Lambda a un problème avec le code (probablement connexion DB).**

---

## ✅ SOLUTION : PYTHON DIRECT (LA PLUS FIABLE)

**Cette méthode fonctionne directement avec la base de données, sans passer par Lambda.**

### Étape 1 : Autoriser votre IP (si pas déjà fait)

1. **Trouvez votre IP** : https://www.whatismyip.com/
2. **Dans AWS RDS** > **mapevent-db** > **Security Groups** > **default**
3. **Vérifiez** qu'il y a une règle avec votre IP/32 (Type PostgreSQL)
4. **Si pas de règle**, ajoutez-la et attendez 1-2 minutes

### Étape 2 : Exécuter le script Python

```powershell
cd C:\MapEventAI_NEW\frontend
python supprimer-comptes.py
```

### Étape 3 : Quand il demande quel compte garder

**Tapez juste Entrée (laissez vide)** pour supprimer TOUS les comptes.

### Étape 4 : Confirmer

**Tapez "OUI"** pour confirmer.

---

## ✅ AVANTAGES DE LA MÉTHODE PYTHON

- ✅ **Plus fiable** (pas de problème Lambda)
- ✅ **Plus rapide** (connexion directe à la DB)
- ✅ **Plus simple** (pas de déploiement)
- ✅ **Fonctionne toujours** si votre IP est autorisée

---

## 🆘 SI VOTRE IP N'EST PAS AUTORISÉE

**Vous devez :**

1. **Trouver votre IP** : https://www.whatismyip.com/
2. **Dans AWS RDS** > **mapevent-db** > **Security Groups** > **default**
3. **Ajouter une règle** :
   - Type : PostgreSQL
   - Source : votre IP/32 (exemple : `81.13.194.194/32`)
   - Port : 5432
4. **Attendre 1-2 minutes**
5. **Réessayez** : `python supprimer-comptes.py`

---

## ✅ RÉSUMÉ

**La méthode Python est la plus fiable :**

1. ✅ Autorisez votre IP dans RDS Security Group (si pas déjà fait)
2. ✅ `cd C:\MapEventAI_NEW\frontend`
3. ✅ `python supprimer-comptes.py`
4. ✅ Tapez Entrée (vide) pour tout supprimer
5. ✅ Tapez "OUI" pour confirmer
6. ✅ C'est tout !

---

**Essayez la méthode Python, c'est la plus simple et la plus fiable !** 🚀


