# 📋 JSON pour la politique du bucket S3

## Copiez-collez ce code dans "Bucket policy"

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

## Où le mettre ?

1. **Console AWS** → **S3** → **Bucket `mapevent-avatars`**
2. **Onglet "Permissions"**
3. **Section "Bucket policy"**
4. **Cliquez "Edit"**
5. **Collez le JSON ci-dessus**
6. **Cliquez "Save changes"**

C'est tout ! ✅




