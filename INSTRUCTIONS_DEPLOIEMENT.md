# Instructions de Déploiement

## ⚠️ IMPORTANT
Les scripts PowerShell doivent être exécutés dans **PowerShell**, **PAS** dans la console du navigateur (F12) !

## Méthode 1 : Via PowerShell (Recommandé)

1. **Ouvrez PowerShell** (pas la console du navigateur)
   - Appuyez sur `Windows + X`
   - Sélectionnez "Windows PowerShell" ou "Terminal"
   - Ou cherchez "PowerShell" dans le menu Démarrer

2. **Naviguez vers le dossier frontend**
   ```powershell
   cd C:\MapEventAI_NEW\frontend
   ```

3. **Exécutez le script de déploiement**
   ```powershell
   .\deploy-force-cache-bust.ps1
   ```

4. **Attendez la fin du déploiement** (1-5 minutes)

5. **Testez dans le navigateur**
   - Ouvrez une fenêtre de navigation privée (Ctrl+Shift+N)
   - Allez sur `https://mapevent.world`
   - L'erreur devrait avoir disparu

## Méthode 2 : Via l'Explorateur de fichiers

1. **Ouvrez l'Explorateur de fichiers**
2. **Naviguez vers** `C:\MapEventAI_NEW\frontend`
3. **Clic droit sur** `deploy-force-cache-bust.ps1`
4. **Sélectionnez** "Exécuter avec PowerShell"
5. **Attendez la fin du déploiement**

## Vérification après déploiement

1. Ouvrez une fenêtre de navigation privée (Ctrl+Shift+N)
2. Allez sur `https://mapevent.world`
3. Ouvrez la console (F12)
4. Vérifiez que les scripts chargés sont `v=20260111-120000` (pas `v=20260107-56`)
5. Vérifiez qu'il n'y a plus d'erreur "SyntaxError: Unexpected token"

## Si le problème persiste

1. Vérifiez que le script s'est bien exécuté (regardez les messages dans PowerShell)
2. Attendez 2-3 minutes supplémentaires (invalidation CloudFront)
3. Videz complètement le cache du navigateur (Ctrl+Shift+Delete)
4. Réessayez dans une fenêtre de navigation privée
