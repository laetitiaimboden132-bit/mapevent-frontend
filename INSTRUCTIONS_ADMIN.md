# 🔐 EXÉCUTER EN TANT QU'ADMINISTRATEUR

## ✅ MÉTHODE SIMPLE

### Étape 1 : Ouvrir PowerShell en administrateur

1. **Appuyez sur** `Windows + X`
2. **Cliquez sur** "Windows PowerShell (Admin)" ou "Terminal (Admin)"
3. **Confirmez** si Windows demande l'autorisation

**OU :**

1. **Tapez "PowerShell"** dans le menu Démarrer
2. **Clic droit** sur "Windows PowerShell"
3. **Cliquez sur** "Exécuter en tant qu'administrateur"
4. **Confirmez** si Windows demande l'autorisation

---

### Étape 2 : Exécuter le script

**Dans PowerShell (administrateur), exécutez :**

```powershell
cd C:\MapEventAI_NEW\frontend
.\DESACTIVER_FIREWALL_TEST.ps1
```

---

## ✅ MÉTHODE ALTERNATIVE : DÉSACTIVER MANUELLEMENT

**Si vous préférez faire manuellement :**

### 1. Désactiver le firewall

**Dans Windows :**
1. **Paramètres** (Windows + I)
2. **Sécurité Windows** > **Pare-feu et protection réseau**
3. **Cliquez sur** "Réseau privé" → **Désactivez** le pare-feu
4. **Cliquez sur** "Réseau public" → **Désactivez** le pare-feu

### 2. Tester la connexion

**Dans PowerShell normal (pas besoin d'admin) :**

```powershell
cd C:\MapEventAI_NEW\frontend
python supprimer-comptes.py
```

### 3. Réactiver le firewall

**Remettez le pare-feu en activant "Réseau privé" et "Réseau public".**

---

## 🎯 RÉSUMÉ

**Méthode 1 (automatique) :**
1. PowerShell en administrateur
2. `cd C:\MapEventAI_NEW\frontend`
3. `.\DESACTIVER_FIREWALL_TEST.ps1`

**Méthode 2 (manuelle) :**
1. Désactiver le firewall dans Paramètres Windows
2. `cd C:\MapEventAI_NEW\frontend`
3. `python supprimer-comptes.py`
4. Réactiver le firewall

---

**Essayez la méthode manuelle, c'est plus simple si vous n'avez pas les droits admin !** 🚀


