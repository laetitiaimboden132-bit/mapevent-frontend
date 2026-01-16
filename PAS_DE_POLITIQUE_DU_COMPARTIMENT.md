# 🔍 Pas de section "Politique du compartiment" ?

## ❓ Pourquoi elle n'apparaît pas ?

La section "Politique du compartiment" (Bucket policy) peut ne pas apparaître si :
- Vous n'avez pas les permissions IAM nécessaires
- L'interface AWS la cache selon vos permissions
- Le bucket est géré par un autre service (CloudFormation, etc.)

---

## 🔍 Ce qu'il faut vérifier

### Étape 1 : Lister toutes les sections dans "Autorisations"

**Dites-moi toutes les sections que vous voyez** dans l'onglet "Autorisations" :

- [ ] Blocage de l'accès public (bucket settings)
- [ ] Partage de ressources entre origines (CORS) ← Vous l'avez déjà
- [ ] Politique du compartiment (Bucket policy) ← Vous ne l'avez pas
- [ ] Liste de contrôle d'accès (ACL)
- [ ] Autres sections ?

---

## ✅ Solution 1 : Utiliser AWS CLI

Si vous avez AWS CLI installé, vous pouvez configurer la Bucket Policy via la ligne de commande :

### Étape 1 : Créer un fichier JSON

1. **Ouvrez le Bloc-notes** (Notepad)
2. **Collez ce code** :

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::mapevent-avatars/avatars/*"
        }
    ]
}
```

3. **Enregistrez le fichier** comme `bucket-policy.json` dans `C:\MapEventAI_NEW\frontend\lambda-package\`

### Étape 2 : Appliquer la politique via PowerShell

1. **Ouvrez PowerShell**
2. **Allez dans le dossier** :

```powershell
cd C:\MapEventAI_NEW\frontend\lambda-package
```

3. **Exécutez cette commande** :

```powershell
aws s3api put-bucket-policy --bucket mapevent-avatars --region eu-west-1 --policy file://bucket-policy.json
```

4. **Si ça fonctionne** → Vous verrez pas d'erreur
5. **Si ça ne fonctionne pas** → Vous verrez une erreur de permissions

---

## ✅ Solution 2 : Vérifier Block Public Access

Même si vous ne voyez pas "Politique du compartiment", vous devriez voir **"Blocage de l'accès public"**.

### Si vous voyez cette section :

1. **Cliquez sur "Modifier"** (si le bouton est actif)
2. **Décochez les 2 premières cases** :
   - Block public access to buckets and objects granted through new access control lists (ACLs)
   - Block public access to buckets and objects granted through any access control lists (ACLs)
3. **Laissez cochées les 2 dernières cases**
4. **Enregistrez**

---

## ✅ Solution 3 : Demander à l'administrateur AWS

Si vous n'avez pas les permissions pour modifier la Bucket Policy :

1. **Contactez l'administrateur AWS** de votre compte
2. **Demandez-lui** de :
   - Vous donner les permissions `s3:PutBucketPolicy` et `s3:GetBucketPolicy`
   - Ou de configurer la Bucket Policy pour vous

---

## 🧪 Test après configuration

Une fois que la Bucket Policy est configurée (via CLI ou par l'admin) :

1. **Testez cette URL** dans votre navigateur :
   ```
   https://mapevent-avatars.s3.eu-west-1.amazonaws.com/avatars/user_1767389921855_75fbd18e9395ca09.jpg
   ```

2. **Résultat** :
   - ✅ **L'image s'affiche** → C'est bon !
   - ❌ **Toujours "Access Denied"** → Il faut aussi modifier Block Public Access

---

## 📋 Checklist

- [ ] J'ai listé toutes les sections dans "Autorisations"
- [ ] J'ai essayé AWS CLI (si installé)
- [ ] J'ai vérifié Block Public Access
- [ ] J'ai contacté l'administrateur AWS (si nécessaire)

---

**Dites-moi toutes les sections que vous voyez dans "Autorisations"** et on trouvera la solution ! 😊




