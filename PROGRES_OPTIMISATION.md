# PROGRÈS OPTIMISATION - map_logic.js

## Statut actuel

- **map_logic.js** : 23 794 lignes → **23 717 lignes** (après suppression closeAuthModal)
- **auth.js** : 2 460 lignes ✅

## Fonctions supprimées

✅ **closeAuthModal()** - lignes 7882-7948 supprimées (~67 lignes)

## Fonctions à supprimer

⏳ **openAuthModal()** - lignes 10343-11112 (~770 lignes) ⚠️ TRÈS LONGUE
⏳ **performRegister()** - lignes 12131-12465 (~335 lignes)
⏳ **performLogin()** - lignes 12467-12587 (~121 lignes)
⏳ **loadSavedUser()** - lignes 19051-19176 (~126 lignes)
⏳ **logout()** - lignes 20286-20347 (~62 lignes)

## Estimation finale

**Total à supprimer** : ~1 481 lignes
**Taille finale estimée** : ~22 313 lignes

## Note importante

Les fonctions sont déjà dans `auth.js` et exposées globalement via `window.*`, donc les appels existants continueront de fonctionner automatiquement.
