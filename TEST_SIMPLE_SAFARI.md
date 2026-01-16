# 🧪 Test Simple - Sans Console

## ✅ Méthode 1 : Vérifier le code source

1. **Ouvrez votre site dans Safari**
2. **Faites un clic droit** sur la page (n'importe où)
3. Cliquez sur **"Afficher la source de la page"** (ou "Show Page Source")
4. Appuyez sur **Cmd+F** (⌘F) pour chercher
5. Tapez : `openAgendaWindow`
6. Si vous trouvez `openAgendaWindow` → Le code est chargé ✅
7. Si vous ne trouvez rien → Le cache bloque ❌

## 🎯 Méthode 2 : Test direct du bouton

1. **Ouvrez votre site**
2. **Connectez-vous** (si nécessaire)
3. **Ouvrez la popup compte** (cliquez sur votre avatar/nom)
4. **Regardez en haut** - vous devriez voir les onglets :
   - 🏠 Accueil
   - 📅 Agenda
   - 👥 Groupes
   - 👥 Amis
   - 🔔 Notifs
5. **Cliquez sur "📅 Agenda"**
6. **Dites-moi ce qui se passe :**
   - ✅ Une fenêtre séparée s'ouvre avec votre agenda
   - ❌ Rien ne se passe
   - ❌ Une erreur apparaît
   - ❌ Le bouton change d'onglet au lieu d'ouvrir une fenêtre

## 🔄 Méthode 3 : Vider le cache Safari (FORCÉ)

1. **Safari** → **Paramètres** → **Avancé**
2. Cliquez sur **"Vider les caches"** (ou "Empty Caches")
3. **Fermez TOUTES les fenêtres Safari** (Cmd+Q)
4. **Rouvrez Safari**
5. Allez sur votre site
6. **Rechargez** : Cmd+Shift+R (⌘⇧R)
7. Testez à nouveau le bouton Agenda

## 📋 Informations à me donner

1. **Voyez-vous les onglets** en haut de la popup compte ?
   - Oui / Non

2. **Quand vous cliquez sur "📅 Agenda", que se passe-t-il ?**
   - Rien
   - Une fenêtre s'ouvre
   - Autre chose (décrivez)

3. **Dans le code source** (Méthode 1), trouvez-vous `openAgendaWindow` ?
   - Oui / Non





