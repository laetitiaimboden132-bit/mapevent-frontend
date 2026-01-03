# Commande PowerShell pour tester create-tables
# Copiez-collez cette commande dans PowerShell

Invoke-WebRequest -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/admin/create-tables" -Method POST -Headers @{"Content-Type"="application/json"} -Body "{}"

