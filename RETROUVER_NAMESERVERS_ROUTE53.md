# 🔍 Retrouver les 4 Name Servers Route 53

## 🎯 Où Aller

### Étape 1 : Aller dans Route 53
- AWS Console → **Route 53**
- **Hosted zones** (Zones hébergées)

### Étape 2 : Trouver/Créer la Zone
- Si vous voyez **`mapevent.world`** → Cliquer dessus
- Si vous ne voyez pas **`mapevent.world`** :
  - Cliquer sur **"Créer une zone hébergée"** (Create hosted zone)
  - **Nom de domaine** : `mapevent.world`
  - **Type** : Public hosted zone
  - Cliquer sur **"Créer une zone hébergée"**

### Étape 3 : Copier les 4 Name Servers
- Cliquer sur la zone **`mapevent.world`**
- Vous verrez une section **"Délégation"** ou **"Name servers"**
- Il y aura **4 Name Servers**, par exemple :
  ```
  ns-1825.awsdns-36.co.uk
  ns-20.awsdns-02.com
  ns-1110.awsdns-10.org
  ns-740.awsdns-28.net
  ```
- **📋 COPIER CES 4 NAMESERVERS**

---

## 📋 Où Trouver les Name Servers dans Route 53

### Option 1 : Section "Délégation"
- En haut de la page de la zone
- Section **"Délégation"** ou **"Delegation"**
- Liste des 4 Name Servers

### Option 2 : Section "Name servers"
- Dans les détails de la zone
- Section **"Name servers"**
- Liste des 4 Name Servers

### Option 3 : Onglet "Délégation"
- Onglet séparé **"Délégation"**
- Liste des 4 Name Servers

---

## 💡 Astuce

**Si vous avez déjà créé la zone auparavant :**
- Les Name Servers sont toujours les mêmes pour cette zone
- Vous pouvez les retrouver dans Route 53 → Hosted zones → mapevent.world

**Si vous n'avez pas encore créé la zone :**
- Il faut la créer d'abord
- Les Name Servers seront générés automatiquement

---

## ✅ Action Immédiate

**Faites ceci MAINTENANT :**

1. **AWS Console** → **Route 53**
2. **Hosted zones**
3. **Créer une zone hébergée** (si pas déjà créée) OU **Cliquer sur mapevent.world**
4. **Copier les 4 Name Servers**
5. **Retourner dans Namecheap** → **Nameservers** → **Custom DNS**
6. **Coller les 4 Name Servers**
7. **Save**

---

## 📝 Format des Name Servers

Les Name Servers Route 53 ressemblent toujours à :
```
ns-XXXX.awsdns-XX.com
ns-XXXX.awsdns-XX.co.uk
ns-XXXX.awsdns-XX.org
ns-XXXX.awsdns-XX.net
```

Ils commencent tous par `ns-` et se terminent par `.awsdns-XX.` avec différentes extensions (.com, .co.uk, .org, .net).

---

## 🆘 Si Vous Ne Trouvez Pas la Zone

**Créer une nouvelle Hosted Zone :**

1. Route 53 → **Hosted zones** → **Créer une zone hébergée**
2. **Nom de domaine** : `mapevent.world`
3. **Type** : Public hosted zone
4. **Créer**
5. Les 4 Name Servers seront affichés automatiquement
6. **Copier les 4 Name Servers**

---

## ✅ Checklist

- [ ] Route 53 → Hosted zones ouvert
- [ ] Zone `mapevent.world` trouvée OU créée
- [ ] Section "Délégation" ou "Name servers" trouvée
- [ ] 4 Name Servers copiés
- [ ] Retour dans Namecheap → Nameservers → Custom DNS
- [ ] 4 Name Servers collés
- [ ] Save



