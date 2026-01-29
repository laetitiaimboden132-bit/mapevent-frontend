# Idées pour alléger le projet (IDE + déploiement)

## 1. Déploiement sans tout charger

- **Fichier à ouvrir en priorité** : `COMMANDE_DEPLOY.txt`  
  Contient les 2 commandes à copier-coller dans PowerShell (frontend puis Lambda). Vous n’avez pas besoin d’ouvrir les gros scripts.

- **Script court** : `deploy-rapide.ps1`  
  Environ 15 lignes. Lance depuis la racine du projet :
  ```powershell
  cd C:\Users\Laeti\.cursor\worktrees\frontend\vpf
  .\deploy-rapide.ps1
  ```
  Il fait uniquement l’upload S3 + invalidation CloudFront (pas les longs checks du script complet).

---

## 2. Alléger l’IDE (Cursor / VSCode)

Si Cursor rame à l’ouverture du projet :

- **Réduire ce qui est indexé**  
  Créer un fichier `.cursorignore` à la racine avec par exemple :
  ```
  lambda-package/lambda-layer-build
  lambda-package/node_modules
  **/SAUVEGARDE_AVANT_GEMINI
  **/*.geojson
  ```
  Cela évite d’indexer des dossiers ou fichiers très lourds.

- **Travailler dans un sous-dossier**  
  Ouvrir seulement `C:\Users\Laeti\.cursor\worktrees\frontend\vpf\public` quand vous modifiez le front (auth.js, map_logic.js, mapevent.html).

- **Éviter d’ouvrir les très gros fichiers**  
  `map_logic.js` (~27 000 lignes) et `auth.js` (~5 600 lignes) : utiliser la recherche (Ctrl+P ou Ctrl+Shift+O) pour aller à une fonction précise au lieu de scroller dans tout le fichier.

---

## 3. Alléger le site (chargement dans le navigateur)

Si c’est la page mapevent.world qui est lente :

- **Cache navigateur**  
  Les `?v=...` dans les scripts forcent le rechargement. Après déploiement, un simple F5 ou “vider le cache” suffit pour prendre la nouvelle version.

- **Découper map_logic.js plus tard**  
  À moyen terme, on pourrait extraire des blocs (auth, carte, liste, modals) dans des fichiers séparés et les charger à la demande. C’est un refactor plus long, mais ça réduit le premier chargement.

---

## 4. Déploiement depuis votre machine

Le déploiement ne peut pas être fait depuis l’assistant (pas d’accès à vos credentials AWS). À faire **chez vous**, dans PowerShell :

1. **Frontend**  
   ```powershell
   cd C:\Users\Laeti\.cursor\worktrees\frontend\vpf
   .\deploy-rapide.ps1
   ```
   ou, si vous préférez le script complet :  
   `.\deploy-frontend.ps1`

2. **Lambda**  
   ```powershell
   cd C:\Users\Laeti\.cursor\worktrees\frontend\vpf\lambda-package
   .\deploy-lambda.ps1
   ```

Si vous voyez “credentials AWS”, exécuter d’abord :  
`aws configure`  
puis relancer les commandes ci‑dessus.
