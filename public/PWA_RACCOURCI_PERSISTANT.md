# Raccourci smartphone (PWA) – Plus persistant

## Modifications effectuées

### 1. `manifest.json`
- **`id`** : ajout de `"id": "https://mapevent.world/mapevent.html"` pour que le navigateur et l’OS reconnaissent toujours la même app, même après mises à jour du manifest. Sans `id` stable, une mise à jour peut être vue comme une « nouvelle » app et le raccourci peut disparaître ou être dupliqué.
- **`start_url`** : passage à une URL **absolue** `"https://mapevent.world/mapevent.html"` au lieu de `"/mapevent.html"`. Ainsi, le raccourci pointe toujours vers la même URL, quel que soit le domaine ou le chemin au moment de l’installation (évite les raccourcis cassés après redirections ou variantes d’URL).

### 2. `mapevent.html`
- **iOS** : ajout de `apple-touch-icon` en 152px et 180px (en plus du 192px) pour une meilleure reconnaissance par l’appareil.
- **Rappel iOS** : petit message discret (une fois par semaine) sur Safari iOS pour rappeler d’ajouter MapEvent à l’écran d’accueil (« Partager → Sur l’écran d’accueil »), au cas où le raccourci aurait été supprimé (mise à jour iOS, nettoyage, etc.).

## Si le raccourci disparaît encore

- **Android** : réinstaller l’app depuis Chrome (menu ⋮ → « Installer l’application » ou « Ajouter à l’écran d’accueil »). Vérifier que le stockage du téléphone n’est pas en mode « optimisation » qui supprime les données des apps « peu utilisées ».
- **iOS** : réajouter via Safari : Partager (carré avec flèche) → « Sur l’écran d’accueil » → Ajouter. Le rappel dans l’app peut réafficher cette consigne une fois par semaine si vous n’êtes pas en mode « ajouté à l’écran d’accueil ».
- **Déploiement** : après déploiement, vider le cache du navigateur ou faire un rechargement forcé sur la page pour que le nouveau `manifest.json` soit pris en compte.
