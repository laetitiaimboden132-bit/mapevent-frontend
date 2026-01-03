# Script de test complet pour tous les endpoints sociaux

$API_BASE = "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api"
$TEST_USER_ID = "test_user_123"
$TEST_FRIEND_ID = "test_friend_456"
$TEST_GROUP_ID = "test_group_789"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTS DES ENDPOINTS SOCIAUX" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Fonction helper pour les requêtes
function Test-Endpoint {
    param(
        [string]$Method,
        [string]$Endpoint,
        [object]$Body = $null,
        [string]$Description
    )
    
    Write-Host "Test: $Description" -ForegroundColor Yellow
    Write-Host "  $Method $Endpoint" -ForegroundColor Gray
    
    try {
        $params = @{
            Uri = "$API_BASE$Endpoint"
            Method = $Method
            ContentType = "application/json"
            ErrorAction = "Stop"
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
        }
        
        $response = Invoke-RestMethod @params
        
        Write-Host "  ✅ Succes" -ForegroundColor Green
        if ($response) {
            Write-Host "  Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
        }
        return $true
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "  ❌ Erreur $statusCode : $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    Write-Host ""
}

# Test 1: Endpoint santé
Write-Host "1. TEST ENDPOINT SANTE" -ForegroundColor Cyan
Test-Endpoint -Method "GET" -Endpoint "/health" -Description "Health check"
Write-Host ""

# Test 2: Envoyer demande d'ami
Write-Host "2. TEST AMIS" -ForegroundColor Cyan
Test-Endpoint -Method "POST" -Endpoint "/social/friends/request" -Body @{
    userId = $TEST_USER_ID
    friendId = $TEST_FRIEND_ID
} -Description "Envoyer demande d'ami"

Test-Endpoint -Method "POST" -Endpoint "/social/friends/accept" -Body @{
    userId = $TEST_FRIEND_ID
    friendId = $TEST_USER_ID
} -Description "Accepter demande d'ami"

Test-Endpoint -Method "GET" -Endpoint "/social/friends?userId=$TEST_USER_ID" -Description "Liste des amis"
Write-Host ""

# Test 3: Créer un groupe
Write-Host "3. TEST GROUPES" -ForegroundColor Cyan
$createGroupResponse = Test-Endpoint -Method "POST" -Endpoint "/social/groups" -Body @{
    name = "Groupe Test"
    description = "Description du groupe test"
    type = "public"
    creatorId = $TEST_USER_ID
    icon = "👥"
} -Description "Creer un groupe"

if ($createGroupResponse) {
    $groupResponse = Invoke-RestMethod -Uri "$API_BASE/social/groups" -Method POST -Body (@{
        name = "Groupe Test"
        description = "Description du groupe test"
        type = "public"
        creatorId = $TEST_USER_ID
        icon = "👥"
    } | ConvertTo-Json) -ContentType "application/json"
    
    if ($groupResponse.groupId) {
        $actualGroupId = $groupResponse.groupId
        
        # Test envoyer message
        Test-Endpoint -Method "POST" -Endpoint "/social/groups/$actualGroupId/messages" -Body @{
            userId = $TEST_USER_ID
            message = "Message de test"
            attachments = @()
        } -Description "Envoyer message dans groupe"
        
        # Test récupérer messages
        Test-Endpoint -Method "GET" -Endpoint "/social/groups/$actualGroupId/messages?userId=$TEST_USER_ID&limit=10" -Description "Recuperer messages"
    }
}
Write-Host ""

# Test 4: Modération d'image
Write-Host "4. TEST MODERATION IMAGE" -ForegroundColor Cyan
Test-Endpoint -Method "POST" -Endpoint "/social/moderation/image" -Body @{
    imageUrl = "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7"
    userId = $TEST_USER_ID
} -Description "Moderer une image"
Write-Host ""

# Test 5: Profil utilisateur
Write-Host "5. TEST PROFILS" -ForegroundColor Cyan
Test-Endpoint -Method "GET" -Endpoint "/social/profile/$TEST_USER_ID" -Description "Recuperer profil utilisateur"

Test-Endpoint -Method "PUT" -Endpoint "/social/profile" -Body @{
    userId = $TEST_USER_ID
    bio = "Bio de test"
    profilePhotos = @("https://images.unsplash.com/photo-1492144534655-ae79c964c9d7")
    profileVideos = @()
    profileLinks = @()
} -Description "Mettre a jour profil"
Write-Host ""

# Test 6: Réactions sur messages
Write-Host "6. TEST REACTIONS" -ForegroundColor Cyan
# Note: Nécessite un messageId réel d'un groupe
Write-Host "  ⚠️  Test necessite un messageId reel (creez un groupe et un message d'abord)" -ForegroundColor Yellow
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTS TERMINES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: Certains tests peuvent echouer si:" -ForegroundColor Yellow
Write-Host "  - La base de donnees n'est pas configuree" -ForegroundColor Yellow
Write-Host "  - Les variables d'environnement ne sont pas definies" -ForegroundColor Yellow
Write-Host "  - Les permissions IAM ne sont pas correctes" -ForegroundColor Yellow
Write-Host ""





