# 🕐 Changer la plage de temps dans CloudWatch Logs

## 📍 Où trouver le sélecteur de temps

### Option 1 : En haut de la page CloudWatch

1. Une fois dans **CloudWatch Logs** > **Log groups** > votre log group > **log stream**
2. En **haut de la page**, vous verrez une barre avec :
   - Un calendrier/icône d'horloge
   - Une plage de temps (ex: "Last 1 hour")
   - Des boutons comme "Refresh"

3. **Cliquez sur la plage de temps** (ex: "Last 1 hour")
4. Un menu déroulant s'ouvre avec les options :
   - Last 5 minutes
   - Last 15 minutes
   - Last 1 hour
   - Last 3 hours
   - Custom range
   - etc.

5. **Sélectionnez "Last 5 minutes"** ou **"Custom range"**

### Option 2 : Si vous ne voyez pas le sélecteur

1. Cherchez en haut à droite de la page
2. Il peut être à côté du bouton "Refresh" (Actualiser)
3. Ou dans une barre d'outils en haut

### Option 3 : Custom range (plage personnalisée)

1. Cliquez sur "Custom range"
2. Sélectionnez :
   - **From (De)** : Il y a 5 minutes
   - **To (À)** : Maintenant
3. Cliquez sur "Apply" (Appliquer)

## 🔄 Après avoir changé la plage

1. Cliquez sur **"Refresh"** (Actualiser) ou appuyez sur **F5**
2. Les logs dans cette plage de temps apparaîtront

## 💡 Astuce

Si vous venez de faire un test, sélectionnez **"Last 5 minutes"** pour voir les logs les plus récents.

## 📍 Localisation exacte

Le sélecteur de temps se trouve généralement :
- **En haut de la page CloudWatch Logs**
- **À droite** du nom du log stream
- **À côté** du bouton "Refresh"
- **Sous** le menu de navigation CloudWatch

Si vous ne le trouvez toujours pas, dites-moi et je vous guiderai autrement !

