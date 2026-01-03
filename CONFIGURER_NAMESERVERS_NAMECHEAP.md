# 🌐 Configurer les Name Servers Route 53 dans Namecheap

## 🎯 Guide Étape par Étape

---

## 📋 Étape 1 : Obtenir les Name Servers Route 53 (Dans AWS)

### 1.1 Aller dans Route 53
- AWS Console → **Route 53**
- **Hosted zones** (Zones hébergées)

### 1.2 Vérifier/Créer la Hosted Zone
- Si vous voyez déjà `mapevent.world` → Cliquer dessus
- Si vous ne voyez pas `mapevent.world` :
  - Cliquer sur **"Créer une zone hébergée"** (Create hosted zone)
  - **Nom de domaine** : `mapevent.world`
  - **Type** : Public hosted zone
  - Cliquer sur **"Créer une zone hébergée"**

### 1.3 Copier les 4 Name Servers
- Cliquer sur la zone `mapevent.world`
- Vous verrez une section **"Délégation"** ou **"Name servers"**
- Il y aura 4 Name Servers, par exemple :
  ```
  ns-1825.awsdns-36.co.uk
  ns-20.awsdns-02.com
  ns-1110.awsdns-10.org
  ns-740.awsdns-28.net
  ```
- **📋 COPIER CES 4 NAMESERVERS** (vous en aurez besoin dans Namecheap)

---

## 📋 Étape 2 : Configurer dans Namecheap

### 2.1 Se Connecter à Namecheap
- Aller sur https://www.namecheap.com
- Se connecter à votre compte

### 2.2 Aller dans Domain List
- Cliquer sur **"Domain List"** (en haut) ou **"Domaines"**
- Vous verrez la liste de vos domaines

### 2.3 Sélectionner mapevent.world
- Trouver **`mapevent.world`** dans la liste
- Cliquer sur **"Manage"** (Gérer) à côté du domaine

### 2.4 Aller dans Advanced DNS
- Dans la page de gestion du domaine
- Cliquer sur l'onglet **"Advanced DNS"** (DNS Avancé)
- OU chercher **"Nameservers"** dans le menu

### 2.5 Modifier les Name Servers
- Chercher la section **"Nameservers"** ou **"Custom DNS"**
- Vous verrez probablement :
  - **"Namecheap BasicDNS"** (par défaut)
  - OU des Name Servers existants

- Cliquer sur **"Custom DNS"** (DNS Personnalisé)
- Vous verrez des champs pour entrer les Name Servers

### 2.6 Entrer les Name Servers Route 53
- **Name Server 1** : Coller le premier (ex: `ns-1825.awsdns-36.co.uk`)
- **Name Server 2** : Coller le deuxième (ex: `ns-20.awsdns-02.com`)
- **Name Server 3** : Coller le troisième (ex: `ns-1110.awsdns-10.org`)
- **Name Server 4** : Coller le quatrième (ex: `ns-740.awsdns-28.net`)

**Important :**
- Entrer les 4 Name Servers
- Vérifier qu'il n'y a pas d'espaces avant/après
- Vérifier l'orthographe

### 2.7 Enregistrer
- Cliquer sur **"Save"** (Enregistrer) ou **"✓"** (coche verte)
- Namecheap va vous confirmer que les modifications sont enregistrées

---

## ⏱️ Étape 3 : Attendre la Propagation

### 3.1 Temps de Propagation
- **Normal** : 15 minutes à 2 heures
- **Maximum** : Jusqu'à 48 heures (rare)

### 3.2 Vérifier la Propagation
- Aller sur https://dnschecker.org
- Chercher : `mapevent.world`
- Sélectionner : **NS** (Name Servers)
- Cliquer sur **"Search"**

**Résultat attendu :**
- Vous devriez voir les 4 Name Servers Route 53 apparaître
- Exemple : `ns-1825.awsdns-36.co.uk`, `ns-20.awsdns-02.com`, etc.

**Si les Name Servers Route 53 apparaissent = ✅ C'est bon !**

---

## ✅ Étape 4 : Après la Propagation

### 4.1 Retourner dans ACM
- AWS Console → Certificate Manager (ACM)
- **Région : us-east-1** (N. Virginia)
- Votre certificat

### 4.2 Créer les Enregistrements DNS
- Cliquer sur votre certificat
- Cliquer sur **"Créer un enregistrement dans Route 53"** (si disponible)
- OU créer manuellement dans Route 53

### 4.3 Attendre la Validation
- 5-30 minutes
- Le statut passera de **"En attente de validation"** à **"Émis"**

---

## 📸 Aperçu de l'Interface Namecheap

**Dans Domain List :**
```
Domain Name          Status    Actions
mapevent.world       Active    [Manage]
```

**Dans Manage → Advanced DNS :**
```
Nameservers
○ Namecheap BasicDNS
● Custom DNS
  [ns-1825.awsdns-36.co.uk    ]
  [ns-20.awsdns-02.com        ]
  [ns-1110.awsdns-10.org      ]
  [ns-740.awsdns-28.net       ]
  [Save] [Cancel]
```

---

## 🐛 Dépannage

### Problème : Je Ne Trouve Pas "Advanced DNS"
- Chercher **"Nameservers"** dans le menu
- OU **"DNS"** → **"Custom DNS"**
- L'interface peut varier selon la version

### Problème : Je Ne Vois Que 2 Champs pour les Name Servers
- Namecheap peut n'afficher que 2 champs
- Entrer les 2 premiers Name Servers Route 53
- Les 2 autres seront ajoutés automatiquement
- OU chercher un bouton **"Add more"** ou **"+"**

### Problème : Les Modifications Ne Sont Pas Enregistrées
- Vérifier que vous êtes bien connecté
- Vérifier que le domaine est actif
- Réessayer après quelques minutes
- Contacter le support Namecheap si nécessaire

---

## ✅ Checklist

- [ ] Route 53 → Hosted Zone créée pour `mapevent.world`
- [ ] 4 Name Servers Route 53 copiés
- [ ] Namecheap → Domain List → `mapevent.world` → Manage
- [ ] Advanced DNS → Custom DNS
- [ ] 4 Name Servers Route 53 entrés
- [ ] Enregistré (Save)
- [ ] Attendu 15 minutes à 2 heures
- [ ] Vérifié sur dnschecker.org que les Name Servers Route 53 apparaissent
- [ ] Retourné dans ACM pour valider le certificat

---

## 🎯 Action Immédiate

**Faites ceci MAINTENANT :**

1. **AWS Route 53** → Copier les 4 Name Servers
2. **Namecheap** → Domain List → `mapevent.world` → Manage
3. **Advanced DNS** → Custom DNS
4. **Coller les 4 Name Servers Route 53**
5. **Save**
6. **Attendre 15 minutes à 2 heures**
7. **Vérifier** sur dnschecker.org
8. **Ensuite** valider le certificat ACM

---

## 💡 Astuce

**Pour vérifier rapidement :**
- Après avoir enregistré dans Namecheap
- Attendre 15-30 minutes
- Aller sur https://dnschecker.org
- Chercher `mapevent.world` avec type **NS**
- Si les Name Servers Route 53 apparaissent = ✅ C'est bon !

**Vous pouvez ensuite valider le certificat ACM !**



