# PLAN D'OPTIMISATION - map_logic.js

## Situation actuelle

- **map_logic.js** : 23 794 lignes ⚠️ TROP VOLUMINEUX
- **auth.js** : 2 460 lignes ✅ BONNE TAILLE

**PROBLÈME** : Les fonctions AUTH sont dupliquées dans map_logic.js alors qu'elles sont déjà dans auth.js et exposées via window.*

## Fonctions à SUPPRIMER de map_logic.js

Ces fonctions sont DÉJÀ dans auth.js et exposées globalement :

1. **closeAuthModal()** - ligne ~7882
2. **openAuthModal()** - ligne ~10413 (très longue, ~600 lignes)
3. **performRegister()** - ligne ~12131 (se termine ~12465)
4. **performLogin()** - ligne ~12467
5. **loadSavedUser()** - ligne ~19051
6. **logout()** - ligne ~20286

## Action requise

**⚠️ ATTENTION** : Ces suppressions doivent être faites MANUELLEMENT et PRUDENTEMENT car :
- Les fonctions font plusieurs centaines de lignes
- Il faut identifier précisément où elles se terminent
- Il faut vérifier qu'elles ne sont plus utilisées localement dans map_logic.js

## Recommandation

**OPTION 1** : Supprimer manuellement les fonctions une par une (long mais sûr)

**OPTION 2** : Utiliser un outil de refactoring automatisé (risqué mais rapide)

**OPTION 3** : Créer un nouveau fichier map_logic_clean.js sans les fonctions AUTH (sécurisé mais nécessite de vérifier toutes les dépendances)

## Prochaines étapes suggérées

1. Identifier précisément les limites de chaque fonction
2. Vérifier qu'elles ne sont plus appelées dans map_logic.js (utiliser window.* à la place)
3. Supprimer les fonctions une par une
4. Tester que tout fonctionne toujours
5. Vérifier la taille finale
