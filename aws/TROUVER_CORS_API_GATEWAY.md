# 🔍 Trouver l'Option CORS dans API Gateway

## 📋 Où Trouver CORS

### Méthode 1 : Menu Actions de la Méthode

1. **Cliquez sur la méthode POST** (pas sur la ressource)
2. **Regardez en haut à droite** de la page de la méthode
3. **Cherchez "Actions"** ou un menu avec 3 points (⋮)
4. **Dans le menu, cherchez :**
   - "Enable CORS" (en anglais)
   - "Activer CORS" (en français)
   - Ou "CORS" tout simplement

---

### Méthode 2 : Onglet "Actions" dans la Méthode

1. **Cliquez sur la méthode POST**
2. **Regardez les onglets** en haut de la page :
   - Method Request
   - Integration Request
   - Integration Response
   - Method Response
   - **Actions** ← C'est peut-être ici !

3. **Cliquez sur l'onglet "Actions"**
4. **Cherchez "Enable CORS"**

---

### Méthode 3 : Configurer CORS Manuellement

**Si vous ne trouvez pas l'option "Enable CORS", configurez-le manuellement :**

#### A. Configurer les Headers dans Method Response

1. **Cliquez sur la méthode POST**
2. **Onglet "Method Response"**
3. **Cliquez sur "200"** (ou créez-le s'il n'existe pas)
4. **Cliquez sur "Add Header"**
5. **Ajoutez ces headers :**
   - `Access-Control-Allow-Origin`
   - `Access-Control-Allow-Headers`
   - `Access-Control-Allow-Methods`

#### B. Configurer les Headers dans Integration Response

1. **Onglet "Integration Response"**
2. **Cliquez sur "200"**
3. **Cliquez sur "Header Mappings"**
4. **Ajoutez :**
   - `Access-Control-Allow-Origin` → `'*'`
   - `Access-Control-Allow-Headers` → `'Content-Type, Authorization'`
   - `Access-Control-Allow-Methods` → `'POST, OPTIONS'`

---

### Méthode 4 : Créer la Méthode OPTIONS (Plus Simple)

**Parfois, créer OPTIONS est plus simple que configurer CORS sur POST :**

1. **Cliquez sur `/api/user/likes`** (la ressource, pas la méthode)
2. **Actions** → **Create Method**
3. **Sélectionnez OPTIONS**
4. **Integration type :** `Mock`
5. **Dans "Integration Response" → "Header Mappings" :**
   ```
   Access-Control-Allow-Origin: '*'
   Access-Control-Allow-Headers: 'Content-Type, Authorization'
   Access-Control-Allow-Methods: 'POST, OPTIONS'
   ```
6. **Response Body :** `{}`
7. **HTTP Status :** `200`
8. **Cliquez sur Save**

**Cette méthode OPTIONS gérera automatiquement CORS pour toutes les méthodes !**

---

## 💡 Astuce : Utiliser le Menu Actions de la Ressource

**Parfois CORS est dans le menu Actions de la RESSOURCE (pas de la méthode) :**

1. **Cliquez sur `/api/user/likes`** (la ressource)
2. **Actions** (en haut à droite)
3. **Cherchez "Enable CORS"** ou "CORS"

**Cette option configure CORS pour toutes les méthodes de la ressource !**

---

## 🎯 Solution la Plus Simple

**Créez la méthode OPTIONS** (Méthode 4 ci-dessus) - c'est souvent plus simple et ça fonctionne à tous les coups !

---

## ✅ Après Avoir Configuré CORS

**N'oubliez pas de :**
1. **Déployer l'API** (Actions → Deploy API)
2. **Tester à nouveau**



