# 🌐 Configurer les Name Servers Route 53 dans le Registrar

## ⚠️ Problème

Vous avez acheté le domaine `mapevent.world` mais les **Name Servers Route 53 ne sont pas encore configurés** dans votre registrar (là où vous avez acheté le domaine).

**Sans les Name Servers Route 53, vous ne pouvez pas :**
- ❌ Valider le certificat ACM
- ❌ Créer les enregistrements DNS
- ❌ Utiliser le domaine avec CloudFront

---

## 🎯 Solution : Configurer les Name Servers

### Étape 1 : Obtenir les Name Servers Route 53

1. **Aller dans AWS Route 53**
   - AWS Console → **Route 53**
   - **Hosted zones** (Zones hébergées)

2. **Vérifier/Créer la Hosted Zone**
   - Si vous ne voyez pas `mapevent.world`, créer une nouvelle hosted zone :
     - Cliquer sur **"Créer une zone hébergée"** (Create hosted zone)
     - **Nom de domaine** : `mapevent.world`
     - **Type** : Public hosted zone
     - Cliquer sur **"Créer une zone hébergée"**

3. **Copier les Name Servers**
   - Cliquer sur la zone `mapevent.world`
   - Vous verrez une section **"Délégation"** ou **"Name servers"**
   - Il y aura 4 Name Servers, par exemple :
     ```
     ns-1825.awsdns-36.co.uk
     ns-20.awsdns-02.com
     ns-1110.awsdns-10.org
     ns-740.awsdns-28.net
     ```
   - **📋 COPIER CES 4 NAMESERVERS**

---

## 📋 Étape 2 : Configurer dans le Registrar

### 2.1 Identifier Votre Registrar

**Où avez-vous acheté mapevent.world ?**
- Namecheap ?
- GoDaddy ?
- Google Domains ?
- OVH ?
- Autre ?

### 2.2 Aller dans les Paramètres DNS

1. **Se connecter** à votre compte chez le registrar
2. **Aller dans "Mes domaines"** ou **"Domaines"**
3. **Cliquer sur `mapevent.world`**
4. **Aller dans "DNS"** ou **"Name Servers"** ou **"Paramètres DNS"**

### 2.3 Modifier les Name Servers

**Option 1 : Name Servers Personnalisés (Recommandé)**
- Chercher **"Name Servers personnalisés"** ou **"Custom Name Servers"**
- Remplacer les Name Servers existants par ceux de Route 53 :
  ```
  ns-1825.awsdns-36.co.uk
  ns-20.awsdns-02.com
  ns-1110.awsdns-10.org
  ns-740.awsdns-28.net
  ```
- **Enregistrer** ou **Appliquer**

**Option 2 : Délégation DNS**
- Chercher **"Délégation DNS"** ou **"DNS Delegation"**
- Mettre les 4 Name Servers Route 53
- **Enregistrer**

---

## ⏱️ Étape 3 : Attendre la Propagation

### 3.1 Temps de Propagation
- **Normal** : 15 minutes à 2 heures
- **Maximum** : Jusqu'à 48 heures (rare)

### 3.2 Vérifier la Propagation
- Aller sur https://dnschecker.org
- Chercher : `mapevent.world`
- Sélectionner : **NS** (Name Servers)
- Vérifier que les 4 Name Servers Route 53 apparaissent

**Si les Name Servers Route 53 apparaissent = ✅ C'est bon !**

---

## ✅ Étape 4 : Après la Propagation

### 4.1 Valider le Certificat ACM

Une fois les Name Servers propagés :

1. **Retourner dans ACM**
   - AWS Console → Certificate Manager
   - Votre certificat

2. **Créer les Enregistrements DNS**
   - Cliquer sur **"Créer un enregistrement dans Route 53"** (si disponible)
   - OU créer manuellement dans Route 53

3. **Attendre la Validation**
   - 5-30 minutes
   - Le statut passera à **"Émis"**

---

## 📋 Checklist Complète

### Configuration Route 53
- [ ] Hosted Zone créée pour `mapevent.world` dans Route 53
- [ ] 4 Name Servers Route 53 copiés

### Configuration Registrar
- [ ] Identifié le registrar (où vous avez acheté le domaine)
- [ ] Connecté à votre compte registrar
- [ ] Trouvé la section DNS/Name Servers
- [ ] Remplacé les Name Servers par ceux de Route 53
- [ ] Enregistré les modifications

### Vérification
- [ ] Attendu 15 minutes à 2 heures
- [ ] Vérifié sur dnschecker.org que les Name Servers Route 53 apparaissent
- [ ] Retourné dans ACM pour valider le certificat

---

## 🆘 Aide par Registrar

### Namecheap
1. **Domain List** → Cliquer sur `mapevent.world` → **Manage**
2. **Advanced DNS** → **Custom DNS**
3. Mettre les 4 Name Servers Route 53
4. **Save**

### GoDaddy
1. **My Products** → **DNS** → `mapevent.world`
2. **Nameservers** → **Change**
3. **Custom** → Mettre les 4 Name Servers Route 53
4. **Save**

### Google Domains
1. **My domains** → `mapevent.world`
2. **DNS** → **Name servers**
3. **Use custom name servers** → Mettre les 4 Name Servers Route 53
4. **Save**

### OVH
1. **Web Cloud** → **Domaines** → `mapevent.world`
2. **Zone DNS** → **Serveurs DNS**
3. Modifier les serveurs DNS → Mettre les 4 Name Servers Route 53
4. **Valider**

---

## 💡 Important

**Ordre des Opérations :**

1. ✅ **D'ABORD** : Configurer les Name Servers Route 53 dans le registrar
2. ✅ **ENSUITE** : Attendre la propagation (15 min - 2h)
3. ✅ **PUIS** : Valider le certificat ACM (créer les enregistrements DNS)
4. ✅ **ENFIN** : Configurer CloudFront avec le certificat

**Ne pas sauter d'étapes !**

---

## 🎯 Action Immédiate

**Faites ceci MAINTENANT :**

1. **Route 53** → Créer une Hosted Zone pour `mapevent.world` (si pas déjà fait)
2. **Copier les 4 Name Servers** Route 53
3. **Aller dans votre registrar** (où vous avez acheté le domaine)
4. **Configurer les Name Servers** avec ceux de Route 53
5. **Attendre 15 minutes à 2 heures**
6. **Vérifier** sur dnschecker.org
7. **Ensuite** valider le certificat ACM

---

## ✅ Résumé

**Le problème :** Les Name Servers Route 53 ne sont pas configurés dans votre registrar.

**La solution :**
1. Obtenir les Name Servers Route 53
2. Les configurer dans votre registrar
3. Attendre la propagation
4. Ensuite valider le certificat

**Sans cette étape, vous ne pourrez pas valider le certificat !**



