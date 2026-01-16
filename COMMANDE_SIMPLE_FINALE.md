# 🚀 SOLUTION FINALE - COMMANDE SIMPLE

## ⚠️ L'ENDPOINT API A UN PROBLÈME (ERREUR 502)

**L'erreur 502 indique que Lambda a un problème avec le code.**

---

## ✅ SOLUTION ALTERNATIVE : PYTHON DIRECT

**Si vous avez autorisé votre IP dans le Security Group RDS, utilisez Python directement :**

### 1. Aller dans le bon dossier :

```powershell
cd C:\MapEventAI_NEW\frontend
```

### 2. Exécuter le script Python :

```powershell
python supprimer-comptes.py
```

### 3. Quand il demande quel compte garder :

**Tapez juste Entrée (laissez vide)** pour supprimer TOUS les comptes.

---

## 🆘 SI VOTRE IP N'EST PAS AUTORISÉE

**Vous devez autoriser votre IP dans AWS :**

1. **Trouvez votre IP** : https://www.whatismyip.com/
2. **Dans AWS RDS** > **mapevent-db** > **Security Groups** > **default**
3. **Ajoutez une règle** : Type PostgreSQL, Source = votre IP/32
4. **Attendez 1-2 minutes**
5. **Réessayez** : `python supprimer-comptes.py`

---

## ✅ RÉSUMÉ

**La méthode Python est la plus fiable :**

1. ✅ Autorisez votre IP dans RDS Security Group
2. ✅ `cd C:\MapEventAI_NEW\frontend`
3. ✅ `python supprimer-comptes.py`
4. ✅ Tapez Entrée (vide) pour tout supprimer
5. ✅ C'est tout !

---

**Essayez la méthode Python, c'est la plus simple et la plus fiable !** 🚀


