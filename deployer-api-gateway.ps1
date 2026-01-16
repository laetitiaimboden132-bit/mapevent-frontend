# Script simple pour deployer l'API Gateway
$API_ID = "j33osy4bvj"
$REGION = "eu-west-1"
$STAGE = "default"

Write-Host "Deploiement de l'API Gateway..." -ForegroundColor Cyan

aws apigateway create-deployment `
    --rest-api-id $API_ID `
    --stage-name $STAGE `
    --description "CORS configuration for /api/user/oauth/google/complete" `
    --region $REGION

Write-Host "Deploiement termine !" -ForegroundColor Green









