# Script pour trouver automatiquement RDS et Redis dans AWS

$REGION = "eu-west-1"

Write-Host "Recherche des ressources AWS..." -ForegroundColor Cyan
Write-Host ""

# Chercher les instances RDS
Write-Host "Recherche des instances RDS..." -ForegroundColor Yellow
try {
    $rdsInstances = aws rds describe-db-instances --region $REGION --query 'DBInstances[*].[DBInstanceIdentifier,Endpoint.Address,Endpoint.Port,MasterUsername]' --output json 2>$null | ConvertFrom-Json
    
    if ($rdsInstances -and $rdsInstances.Count -gt 0) {
        Write-Host "Instances RDS trouvees:" -ForegroundColor Green
        for ($i = 0; $i -lt $rdsInstances.Count; $i++) {
            $instance = $rdsInstances[$i]
            Write-Host "  [$i] $($instance[0])" -ForegroundColor Cyan
            Write-Host "      Host: $($instance[1])" -ForegroundColor Gray
            Write-Host "      Port: $($instance[2])" -ForegroundColor Gray
            Write-Host "      User: $($instance[3])" -ForegroundColor Gray
        }
        
        if ($rdsInstances.Count -eq 1) {
            $selectedRDS = $rdsInstances[0]
            $RDS_HOST = $selectedRDS[1]
            $RDS_PORT = $selectedRDS[2]
            $RDS_USER = $selectedRDS[3]
            Write-Host ""
            Write-Host "Utilisation de l'instance unique: $($selectedRDS[0])" -ForegroundColor Green
        } else {
            $choice = Read-Host "Selectionnez une instance (0-$($rdsInstances.Count-1))"
            $selectedRDS = $rdsInstances[[int]$choice]
            $RDS_HOST = $selectedRDS[1]
            $RDS_PORT = $selectedRDS[2]
            $RDS_USER = $selectedRDS[3]
        }
    } else {
        Write-Host "Aucune instance RDS trouvee dans la region $REGION" -ForegroundColor Yellow
        Write-Host "Vous devez creer une instance RDS PostgreSQL:" -ForegroundColor Yellow
        Write-Host "  aws rds create-db-instance --db-instance-identifier mapevent-db --db-instance-class db.t3.micro --engine postgres --master-username admin --master-user-password VotreMotDePasse --allocated-storage 20 --region $REGION" -ForegroundColor Gray
        $RDS_HOST = Read-Host "Entrez manuellement RDS_HOST"
        $RDS_PORT = Read-Host "Entrez RDS_PORT (defaut: 5432)" 
        if ([string]::IsNullOrWhiteSpace($RDS_PORT)) { $RDS_PORT = "5432" }
        $RDS_USER = Read-Host "Entrez RDS_USER"
    }
} catch {
    Write-Host "Erreur lors de la recherche RDS: $($_.Exception.Message)" -ForegroundColor Red
    $RDS_HOST = Read-Host "Entrez manuellement RDS_HOST"
    $RDS_PORT = Read-Host "Entrez RDS_PORT (defaut: 5432)"
    if ([string]::IsNullOrWhiteSpace($RDS_PORT)) { $RDS_PORT = "5432" }
    $RDS_USER = Read-Host "Entrez RDS_USER"
}

Write-Host ""

# Chercher les clusters ElastiCache (Redis)
Write-Host "Recherche des clusters ElastiCache (Redis)..." -ForegroundColor Yellow
try {
    # Utiliser --show-cache-node-info pour obtenir les endpoints
    $redisClustersRaw = aws elasticache describe-cache-clusters --region $REGION --show-cache-node-info --query 'CacheClusters[*].[CacheClusterId,CacheNodes[0].Endpoint.Address,CacheNodes[0].Endpoint.Port]' --output json 2>$null | ConvertFrom-Json
    
    if ($redisClustersRaw -and $redisClustersRaw.Count -gt 0) {
        Write-Host "Clusters Redis trouves:" -ForegroundColor Green
        $redisClusters = @()
        for ($i = 0; $i -lt $redisClustersRaw.Count; $i++) {
            $cluster = $redisClustersRaw[$i]
            if ($cluster -and $cluster.Count -ge 3 -and $cluster[1]) {
                $redisClusters += ,@($cluster[0], $cluster[1], $cluster[2])
                Write-Host "  [$i] $($cluster[0])" -ForegroundColor Cyan
                Write-Host "      Host: $($cluster[1])" -ForegroundColor Gray
                Write-Host "      Port: $($cluster[2])" -ForegroundColor Gray
            }
        }
        
        if ($redisClusters.Count -eq 1) {
            $selectedRedis = $redisClusters[0]
            $REDIS_HOST = $selectedRedis[1]
            $REDIS_PORT = $selectedRedis[2]
            Write-Host ""
            Write-Host "Utilisation du cluster unique: $($selectedRedis[0])" -ForegroundColor Green
        } elseif ($redisClusters.Count -gt 1) {
            Write-Host ""
            Write-Host "Selectionnez un cluster (0-$($redisClusters.Count-1)):" -ForegroundColor Yellow
            $choice = Read-Host "Numero"
            if ($choice -match '^\d+$' -and [int]$choice -lt $redisClusters.Count) {
                $selectedRedis = $redisClusters[[int]$choice]
                $REDIS_HOST = $selectedRedis[1]
                $REDIS_PORT = $selectedRedis[2]
            } else {
                Write-Host "Choix invalide, utilisation du premier cluster" -ForegroundColor Yellow
                $selectedRedis = $redisClusters[0]
                $REDIS_HOST = $selectedRedis[1]
                $REDIS_PORT = $selectedRedis[2]
            }
        } else {
            Write-Host "Aucun endpoint Redis valide trouve" -ForegroundColor Yellow
            $REDIS_HOST = ""
            $REDIS_PORT = "6379"
        }
    } else {
        Write-Host "Aucun cluster Redis trouve dans la region $REGION" -ForegroundColor Yellow
        Write-Host "Vous devez creer un cluster ElastiCache Redis:" -ForegroundColor Yellow
        Write-Host "  aws elasticache create-cache-cluster --cache-cluster-id mapevent-redis --cache-node-type cache.t3.micro --engine redis --num-cache-nodes 1 --region $REGION" -ForegroundColor Gray
        $REDIS_HOST = ""
        $REDIS_PORT = "6379"
    }
} catch {
    Write-Host "Erreur lors de la recherche Redis: $($_.Exception.Message)" -ForegroundColor Red
    $REDIS_HOST = ""
    $REDIS_PORT = "6379"
}

Write-Host ""

# Demander le mot de passe RDS seulement si pas déjà défini
if ([string]::IsNullOrWhiteSpace($RDS_PASSWORD)) {
    try {
        $RDS_PASSWORD = Read-Host "Entrez RDS_PASSWORD" -AsSecureString
        $RDS_PASSWORD_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($RDS_PASSWORD))
    } catch {
        Write-Host "Mode non-interactif detecte. Utilisez la variable d'environnement RDS_PASSWORD ou editez lambda.env manuellement." -ForegroundColor Yellow
        $RDS_PASSWORD_PLAIN = ""
    }
} else {
    $RDS_PASSWORD_PLAIN = $RDS_PASSWORD
}

# Mettre à jour lambda.env
$envFile = "lambda.env"
if (-not (Test-Path $envFile)) {
    Copy-Item "lambda.env.example" $envFile
}

Write-Host "Mise a jour de $envFile..." -ForegroundColor Yellow

$content = Get-Content $envFile -Raw

# Remplacer les valeurs
$content = $content -replace 'RDS_HOST=.*', "RDS_HOST=$RDS_HOST"
$content = $content -replace 'RDS_PORT=.*', "RDS_PORT=$RDS_PORT"
$content = $content -replace 'RDS_DB=.*', "RDS_DB=mapevent"
$content = $content -replace 'RDS_USER=.*', "RDS_USER=$RDS_USER"
$content = $content -replace 'RDS_PASSWORD=.*', "RDS_PASSWORD=$RDS_PASSWORD_PLAIN"
$content = $content -replace 'REDIS_HOST=.*', "REDIS_HOST=$REDIS_HOST"
$content = $content -replace 'REDIS_PORT=.*', "REDIS_PORT=$REDIS_PORT"

Set-Content -Path $envFile -Value $content -NoNewline

Write-Host ""
Write-Host "✅ Configuration mise a jour dans $envFile" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaine etape: Executez .\configure_lambda_env.ps1" -ForegroundColor Cyan

