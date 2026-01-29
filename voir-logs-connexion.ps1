# Script pour voir les logs CloudWatch liés à la CONNEXION (pour diagnostiquer "pas pu me connecter")
# Usage: .\voir-logs-connexion.ps1 [-Minutes 15]

param(
    [int]$Minutes = 15
)

$FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"
$LOG_GROUP = "/aws/lambda/$FUNCTION_NAME"
$OUTPUT_FILE = "lambda-package\logs-connexion.txt"

# Mots-clés liés à la connexion à rechercher dans les logs
$CONNEXION_KEYWORDS = @(
    "Connexion RDS",
    "Erreur connexion",
    "Connexion DB",
    "oauth",
    "user/me",
    "user/oauth",
    "ERROR",
    "Traceback",
    "Exception",
    "502",
    "CORS",
    "require_auth",
    "Bearer",
    "Token",
    "login",
    "register",
    "INIT_START",
    "START RequestId",
    "END RequestId",
    "REPORT RequestId"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "LOGS CONNEXION - $FUNCTION_NAME (dernières $Minutes min)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$tempFile = Join-Path $env:TEMP "lambda-logs-connexion-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"
try {
    $env:AWS_PAGER = ""
    $env:PYTHONIOENCODING = "utf-8"
    aws logs tail $LOG_GROUP --since "${Minutes}m" --region $REGION --format short 2>&1 | Out-File -FilePath $tempFile -Encoding UTF8 -Force

    if (-not (Test-Path $tempFile)) {
        Write-Host "ERREUR: Impossible de creer le fichier de logs" -ForegroundColor Red
        exit 1
    }

    $allLines = Get-Content $tempFile -Encoding UTF8 -ErrorAction SilentlyContinue
    if (-not $allLines) {
        Write-Host "Aucun log recupere. Verifiez AWS CLI et la region $REGION." -ForegroundColor Yellow
        Write-Host "  aws logs tail $LOG_GROUP --since ${Minutes}m --region $REGION --format short" -ForegroundColor Gray
        exit 0
    }

    # Filtrer les lignes contenant un mot-clé connexion
    $pattern = ($CONNEXION_KEYWORDS | ForEach-Object { [regex]::Escape($_) }) -join "|"
    $connexionLines = $allLines | Where-Object { $_ -match $pattern }

    if ($connexionLines) {
        Write-Host "Lignes liees a la connexion:" -ForegroundColor Green
        Write-Host ""
        $connexionLines | ForEach-Object {
            if ($_ -match "ERROR|Traceback|Exception|Erreur|502") {
                Write-Host $_ -ForegroundColor Red
            } elseif ($_ -match "Connexion RDS reussie|oauth|user/me") {
                Write-Host $_ -ForegroundColor Green
            } else {
                Write-Host $_ -ForegroundColor Gray
            }
        }
        Write-Host ""
    } else {
        Write-Host "Aucune ligne 'connexion' trouvee. Affichage des 30 dernieres lignes brutes:" -ForegroundColor Yellow
        Write-Host ""
        $allLines | Select-Object -Last 30 | ForEach-Object { Write-Host $_ -ForegroundColor Gray }
    }

    # Sauvegarder aussi dans le projet pour analyse
    $outPath = Join-Path $PSScriptRoot $OUTPUT_FILE
    $allLines | Set-Content -Path $outPath -Encoding UTF8 -Force
    Write-Host ""
    Write-Host "Logs complets (UTF-8) sauvegardes dans:" -ForegroundColor Cyan
    Write-Host "   $outPath" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Pour ouvrir:  code $outPath   ou   notepad $outPath" -ForegroundColor Cyan
    Write-Host "Recherchez: Connexion RDS | Erreur connexion | oauth | user/me | ERROR | Traceback" -ForegroundColor Gray

} catch {
    Write-Host "ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifiez: 1) AWS CLI installe  2) aws configure  3) Region eu-west-1" -ForegroundColor Yellow
    Write-Host "Console: CloudWatch > Log groups > $LOG_GROUP" -ForegroundColor Gray
    exit 1
}
