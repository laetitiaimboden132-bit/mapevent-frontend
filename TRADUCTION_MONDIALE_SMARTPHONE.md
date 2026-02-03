# Traduction mondiale & version smartphone MapEvent

## Ce qui existe déjà

- **Langues supportées** (105 – meilleure au monde) : FR, EN, ES, ZH, HI, DE, IT, PT, RU, AR, JA, KO, NL, TR, PL, VI, ID, TH, UK, SV, NO, DA, FI, EL, HE, RO, MS, CS, HU, SK, BG, HR, SR, LT, LV, ET, SL, TA, BN, UR, FA, MR, SW, AM, AF, CA, PA, TL, MY, NE, IS, SQ, MK, BS, GL, CY, KA, HY, AZ, KK, UZ, ML, TE, GU, KN, SI, EU, MN, GA, LB, MT, YO, HA, IG, SO, RW, MG, WO, ST, TN, XH, ZU, KM, LO, SD, PS, KY, TK, TG, BR, GD, FY, KU, HT, JV, SU, NY, OM, TI, DV, BO, DZ, OR, AS, KMR, CKB.
- **Fonction** : `window.t("cle")` retourne la traduction pour la langue courante (fallback : FR puis EN).
- **Variable** : `currentLanguage` (code à 2 lettres).
- **Changement de langue** : `setLanguage("en")` met à jour l’UI et enregistre dans `localStorage` (`mapEventLanguage`).
- **Dictionnaires** : `window.translations[code]` dans `map_logic.js` (`translationsDataObject` + héritage EN pour les langues partielles).

## Pour la version smartphone dans le monde entier

### 1. Comment la langue est choisie (surtout smartphone)

C’est déjà en place dans `initLanguage()` via `detectUserLanguage()` :

1. **Langue sauvegardée** : si l’utilisateur a déjà choisi une langue, on lit `localStorage.getItem("mapEventLanguage")` et on l’utilise.
2. **Langue du téléphone / navigateur** : sinon on utilise la langue du système :
   - **Sur smartphone** : le navigateur (Chrome, Safari, etc.) expose la **langue du téléphone** dans `navigator.language` (ex. `"fr-FR"`, `"en-US"`, `"ja-JP"`). On en prend le code à 2 lettres (`fr`, `en`, `ja`).
   - **Sur desktop** : pareil, c’est la langue préférée du navigateur.
3. **Fallback** : si ce code n’est pas dans la liste des langues supportées, on utilise l’anglais (`"en"`).

Donc **sur smartphone, dès la première visite**, l’app affiche la langue du téléphone si elle est supportée, sinon l’anglais. Dès que l’utilisateur change la langue dans l’app, ce choix est sauvegardé et réutilisé aux prochaines visites.

### 2. Ajouter une nouvelle langue (ex. allemand, arabe, portugais)

1. Dans `map_logic.js`, ajouter la clé au dictionnaire global, par ex. `de: { ... }` ou `ar: { ... }`.
2. Étendre `window.translations` : `window.translations.de = { ... };`
3. Dans le sélecteur de langue (topbar), ajouter l’option (drapeau + code langue).
4. Dans `setLanguage()`, accepter le nouveau code (ex. `"de"`, `"ar"`) et l’enregistrer dans `localStorage`.

Les clés doivent être les mêmes que en FR/EN (ex. `"filter"`, `"add_to_agenda"`, etc.).

### 3. Utiliser les traductions partout (y compris discussion & modales)

- Remplacer les chaînes en dur par `window.t("cle")`.
- Exemple : au lieu de `"J'aime"` / `"Commenter"` en dur dans la discussion, utiliser `window.t("like")` et une clé du type `"comment"` ou `"comment_action"` si tu l’ajoutes au dictionnaire.

Ajouter les clés manquantes pour la discussion, par ex. :

- `"discussion"`, `"write_comment"`, `"publish"`, `"like"`, `"comment"`, `"reply"`, `"ago_min"`, `"ago_h"`, `"ago_d"`, etc.

### 4. Version smartphone (responsive + UX)

- **Même code i18n** : `currentLanguage` et `window.t()` fonctionnent pareil sur mobile.
- **Viewport** : `meta viewport` déjà présent dans `mapevent.html`.
- **Modales / discussion** : utiliser `max-width: 100%`, `max-height: 100vh` ou `90vh`, et `overflow-y: auto` pour que la discussion reste lisible sur petit écran.
- **Sélecteur de langue** : le garder dans la topbar ou dans le menu “Compte” sur mobile pour que l’utilisateur puisse changer de langue partout dans le monde.

### 5. Résumé des étapes “traduction monde entier”

| Étape | Action |
|-------|--------|
| 1 | Détecter la langue au démarrage (sauvegardée puis `navigator.language`) et appeler `setLanguage(...)`. |
| 2 | Ajouter des langues dans `translationsDataObject` et dans le sélecteur (FR, EN, ES, ZH, HI + DE, AR, PT, etc.). |
| 3 | Remplacer toutes les chaînes visibles par `window.t("cle")` et ajouter les clés manquantes (discussion, erreurs, etc.). |
| 4 | Sur smartphone : même logique ; s’assurer que les modales et la discussion sont responsive (taille, scroll). |

En suivant ça, la version smartphone peut afficher la bonne langue partout dans le monde, avec possibilité de changer de langue à tout moment.
