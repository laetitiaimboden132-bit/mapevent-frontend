# 🔥 TESTER SANS FIREWALL WINDOWS

## 🎯 SOLUTION RAPIDE

**Le firewall Windows peut bloquer la connexion PostgreSQL.**

---

## ✅ MÉTHODE 1 : SCRIPT AUTOMATIQUE (RECOMMANDÉ)

**J'ai créé un script qui fait tout automatiquement :**

1. **Ouvrez PowerShell en tant qu'administrateur** :
   - Clic droit sur PowerShell
   - "Exécuter en tant qu'administrateur"

2. **Exécutez** :
   ```powershell
   cd C:\MapEventAI_NEW\frontend
   .\DESACTIVER_FIREWALL_TEST.ps1
   ```

**Le script va :**
- ✅ Désactiver temporairement le firewall
- ✅ Tester la connexion
- ✅ Réactiver automatiquement le firewall

---

## ✅ MÉTHODE 2 : MANUEL

### Désactiver le firewall

**Dans Windows :**
1. **Paramètres** (Windows + I)
2. **Sécurité Windows** > **Pare-feu et protection réseau**
3. **Désactivez** pour "Réseau privé" et "Réseau public"

**OU via PowerShell (administrateur) :**
```powershell
Set-NetFirewallProfile -Profile Domain,Private,Public -Enabled False
```

### Tester la connexion

```powershell
cd C:\MapEventAI_NEW\frontend
python supprimer-comptes.py
```

### Réactiver le firewall

**Via PowerShell (administrateur) :**
```powershell
Set-NetFirewallProfile -Profile Domain,Private,Public -Enabled True
```

---

## ✅ MÉTHODE 3 : AUTORISER POSTGRESQL PERMANENTEMENT

**Si le test fonctionne, vous pouvez autoriser PostgreSQL en permanence :**

**Via PowerShell (administrateur) :**
```powershell
New-NetFirewallRule -DisplayName "PostgreSQL" -Direction Inbound -Protocol TCP -LocalPort 5432 -Action Allow
```

---

## 🎯 RÉSUMÉ

1. ✅ **Ouvrez PowerShell en administrateur**
2. ✅ **Exécutez** : `.\DESACTIVER_FIREWALL_TEST.ps1`
3. ✅ **Le script fait tout automatiquement**

---

**Essayez le script automatique, c'est le plus simple !** 🚀


