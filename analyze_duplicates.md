# ANALYSE DES DOUBLONS - map_logic.js

## Situation actuelle

- **map_logic.js** : 23 794 lignes ⚠️ TROP VOLUMINEUX
- **auth.js** : 2 460 lignes ✅ BONNE TAILLE

## Fonctions AUTH dupliquées détectées dans map_logic.js

Ces fonctions sont déjà dans auth.js et exposées via window.*, elles doivent être SUPPRIMÉES de map_logic.js :

1. **closeAuthModal()** - ligne ~7882 (déjà dans auth.js)
2. **openAuthModal()** - ligne ~10413 (déjà dans auth.js, ~600 lignes)
3. **performRegister()** - ligne ~12131 (déjà dans auth.js)
4. **performLogin()** - ligne ~12467 (déjà dans auth.js)
5. **loadSavedUser()** - ligne ~19051 (déjà dans auth.js)
6. **logout()** - ligne ~20286 (déjà dans auth.js)

## Plan d'action

### Phase 1 : Identifier les limites exactes de chaque fonction
- Trouver où chaque fonction se termine dans map_logic.js
- Vérifier qu'elles ne sont plus appelées localement dans map_logic.js
- Vérifier qu'elles sont bien exposées dans auth.js

### Phase 2 : Supprimer les fonctions une par une
- Supprimer closeAuthModal() (~70 lignes)
- Supprimer openAuthModal() (~600 lignes)
- Supprimer performRegister() (~300 lignes)
- Supprimer performLogin() (~200 lignes)
- Supprimer loadSavedUser() (~125 lignes)
- Supprimer logout() (~60 lignes)

**Total estimé à supprimer : ~1 355 lignes**

### Phase 3 : Vérification
- Vérifier que map_logic.js compile toujours
- Vérifier que les fonctions sont toujours accessibles via window.*
- Vérifier la taille finale de map_logic.js

## Estimation finale

Après suppression : ~22 439 lignes (toujours volumineux mais mieux)
