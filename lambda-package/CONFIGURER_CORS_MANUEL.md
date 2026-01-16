# 🔧 Configuration CORS manuelle pour mapevent-avatars

## Configuration JSON à copier-coller

Copiez exactement ce code dans la section CORS de votre bucket S3 :

```json
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET",
            "HEAD"
        ],
        "AllowedOrigins": [
            "*"
        ],
        "ExposeHeaders": [
            "ETag",
            "Content-Length",
            "Content-Type"
        ],
        "MaxAgeSeconds": 3600
    }
]
```

## Instructions rapides

1. Console AWS → S3 → Bucket `mapevent-avatars`
2. Onglet **Permissions**
3. Section **Cross-origin resource sharing (CORS)**
4. Cliquez **Edit** (Modifier)
5. Collez le JSON ci-dessus
6. Cliquez **Save changes** (Enregistrer)

C'est tout ! ✅




