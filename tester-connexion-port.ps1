# Test de connexion au port 5432

$hostname = "mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com"
$port = 5432

Write-Host "Test de connexion au port $port..." -ForegroundColor Cyan
Write-Host "Host: $hostname" -ForegroundColor Yellow
Write-Host ""

try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $connection = $tcpClient.BeginConnect($hostname, $port, $null, $null)
    $wait = $connection.AsyncWaitHandle.WaitOne(5000, $false)
    
    if ($wait) {
        $tcpClient.EndConnect($connection)
        Write-Host "SUCCES: Le port $port est accessible!" -ForegroundColor Green
        $tcpClient.Close()
    } else {
        Write-Host "TIMEOUT: Le port $port n'est pas accessible (timeout après 5 secondes)" -ForegroundColor Red
        Write-Host ""
        Write-Host "Causes possibles:" -ForegroundColor Yellow
        Write-Host "  1. La propagation réseau n'est pas encore complete" -ForegroundColor White
        Write-Host "  2. Le firewall Windows bloque la connexion" -ForegroundColor White
        Write-Host "  3. La regle Security Group n'est pas encore appliquee" -ForegroundColor White
        $tcpClient.Close()
    }
} catch {
    Write-Host "ERREUR: $($_.Exception.Message)" -ForegroundColor Red
}


