# 🔄 Méthode alternative pour Firefox

## Si vous ne trouvez pas la zone de saisie

### Méthode 1 : Utiliser l'onglet "Console" directement

1. **Ouvrez la console** (F12)
2. **Cliquez sur l'onglet "Console"** en haut
3. **Regardez en bas** → Il y a une barre avec `>` ou une zone de texte
4. **Cliquez dedans** et tapez : `currentUser.profilePhoto`
5. **Entrée**

---

### Méthode 2 : Utiliser l'inspecteur

1. **Ouvrez la console** (F12)
2. **Onglet "Inspecteur"** (ou "Inspector")
3. **En bas**, il y a une zone de saisie
4. **Tapez** : `currentUser.profilePhoto`
5. **Entrée**

---

### Méthode 3 : Utiliser Scratchpad (éditeur de code)

1. **Menu Firefox** (☰) → **Outils de développement web**
2. **"Scratchpad"** (ou "Bloc-notes")
3. **Tapez** :
   ```javascript
   console.log(currentUser.profilePhoto);
   ```
4. **Appuyez sur** `Ctrl+R` (ou `Cmd+R` sur Mac) pour exécuter
5. **Regardez la console** pour voir le résultat

---

## 🎯 La méthode la plus simple

**Essayez cette méthode** :

1. **F12** pour ouvrir la console
2. **Regardez EN BAS** de la fenêtre de la console
3. **Vous devriez voir** quelque chose comme :
   ```
   ┌─────────────────────────┐
   │  Console                │
   ├─────────────────────────┤
   │  [messages]             │
   │                         │
   ├─────────────────────────┤
   │  >                      │  ← ICI !
   └─────────────────────────┘
   ```

4. **Cliquez après le `>`** et tapez : `currentUser.profilePhoto`
5. **Entrée**

---

**Dites-moi si vous voyez maintenant le `>` en bas de la console !** 😊




