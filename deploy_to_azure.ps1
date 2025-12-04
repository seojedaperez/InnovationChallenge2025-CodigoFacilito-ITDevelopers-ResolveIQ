# Script de Despliegue Automático a Azure
# Este script automatiza el proceso de despliegue descrito en DEPLOYMENT_GUIDE.md

$ErrorActionPreference = "Stop"

# Configurar encoding para evitar errores de Unicode en Windows
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

function Write-Color($text, $color) {
    Write-Host $text -ForegroundColor $color
}

# 1. Verificar Azure CLI
if (-not (Get-Command "az" -ErrorAction SilentlyContinue)) {
    Write-Color "Error: Azure CLI ('az') no está instalado o no está en el PATH." "Red"
    Write-Color "Por favor instala Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" "Yellow"
    exit 1
}

# 2. Cargar variables de entorno del backend
Write-Color "Cargando variables de entorno..." "Cyan"
$BackendEnv = @{}
if (Test-Path "backend\.env") {
    Get-Content "backend\.env" | ForEach-Object {
        if ($_ -match "^([^#=]+)=(.*)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim().Trim('"')
            $BackendEnv[$key] = $value
        }
    }
}
else {
    Write-Color "Error: No se encontró backend\.env" "Red"
    exit 1
}

# Configuración Base
$ResourceGroup = "rg-service-desk-agents"
$Location = "eastus2"
$AcrName = "acrservicedesk" + (Get-Random -Minimum 1000 -Maximum 9999)
$AcaEnv = "aca-env-servicedesk"
$BackendAppName = "backend-api"
$FrontendAppName = "frontend-ui"

# 3. Iniciar Sesión
Write-Color "Iniciando sesión en Azure..." "Cyan"
if ($BackendEnv.ContainsKey("AZURE_AD_TENANT_ID")) {
    Write-Color "Usando Tenant ID: $($BackendEnv['AZURE_AD_TENANT_ID'])" "Cyan"
    az login --tenant $BackendEnv['AZURE_AD_TENANT_ID']
}
else {
    az login
}

# 3.1 Registrar Proveedores de Recursos Necesarios
Write-Color "Verificando registro de proveedores de recursos..." "Cyan"
$providers = @("Microsoft.ContainerRegistry", "Microsoft.App", "Microsoft.OperationalInsights")
foreach ($provider in $providers) {
    $state = az provider show --namespace $provider --query "registrationState" -o tsv
    if ($state -ne "Registered") {
        Write-Color "Registrando proveedor $provider..." "Yellow"
        az provider register --namespace $provider
        
        # Esperar a que se registre
        Write-Color "Esperando a que se complete el registro de $provider (esto puede tardar unos minutos)..." "Yellow"
        $retries = 0
        while ($state -ne "Registered" -and $retries -lt 30) {
            Start-Sleep -Seconds 10
            $state = az provider show --namespace $provider --query "registrationState" -o tsv
            $retries++
        }
        
        if ($state -ne "Registered") {
            Write-Color "Error: No se pudo registrar $provider. Por favor regístralo manualmente en el Portal de Azure." "Red"
            exit 1
        }
        Write-Color "$provider registrado exitosamente." "Green"
    }
    else {
        Write-Color "$provider ya está registrado." "Green"
    }
}

# 4. Crear Grupo de Recursos
Write-Color "Creando Grupo de Recursos '$ResourceGroup'..." "Cyan"
az group create --name $ResourceGroup --location $Location

# 5. Crear ACR
Write-Color "Creando Azure Container Registry '$AcrName'..." "Cyan"
# Verificar si ya existe para evitar errores
$acrExists = az acr list --resource-group $ResourceGroup --query "[?name=='$AcrName'].id" -o tsv
if (-not $acrExists) {
    az acr create --resource-group $ResourceGroup --name $AcrName --sku Basic --admin-enabled true
}
else {
    Write-Color "ACR '$AcrName' ya existe." "Yellow"
}

# Obtener credenciales ACR con reintentos
Write-Color "Obteniendo credenciales de ACR..." "Cyan"
$AcrPassword = $null
$retries = 0
while (-not $AcrPassword -and $retries -lt 5) {
    try {
        $AcrPassword = az acr credential show --name $AcrName --query "passwords[0].value" -o tsv 2>$null
    }
    catch {
        Write-Color "Reintentando obtener credenciales..." "Yellow"
    }
    if (-not $AcrPassword) {
        Start-Sleep -Seconds 5
        $retries++
    }
}

if (-not $AcrPassword) {
    Write-Color "Error: No se pudieron obtener las credenciales del ACR. El despliegue no puede continuar." "Red"
    exit 1
}

# 6. Build & Push Backend
Write-Color "Construyendo y subiendo imagen Backend..." "Cyan"
Push-Location backend
az acr build --registry $AcrName --image backend:latest . --no-logs
if ($LASTEXITCODE -ne 0) {
    Write-Color "Error construyendo imagen de Backend." "Red"
    Pop-Location
    exit 1
}
Pop-Location

# 7. Crear Entorno Container Apps (Necesario antes de desplegar backend)
Write-Color "Creando Entorno de Container Apps..." "Cyan"
az containerapp env create --name $AcaEnv --resource-group $ResourceGroup --location $Location

# 8. Desplegar Backend (Para obtener URL)
Write-Color "Desplegando Backend..." "Cyan"
# Construir string de variables de entorno
$EnvVars = @()
$BackendEnv.Keys | ForEach-Object {
    $val = $BackendEnv[$_]
    $EnvVars += "$_=$val"
}

# Asegurar que el backend app exista o crearlo
az containerapp create `
    --name $BackendAppName `
    --resource-group $ResourceGroup `
    --environment $AcaEnv `
    --image "$AcrName.azurecr.io/backend:latest" `
    --target-port 5000 `
    --ingress external `
    --registry-server "$AcrName.azurecr.io" `
    --registry-username $AcrName `
    --registry-password $AcrPassword `
    --env-vars $EnvVars `
    --query properties.configuration.ingress.fqdn -o tsv

$BackendUrl = az containerapp show --name $BackendAppName --resource-group $ResourceGroup --query properties.configuration.ingress.fqdn -o tsv
if (-not $BackendUrl) {
    Write-Color "Error: No se pudo obtener la URL del Backend." "Red"
    exit 1
}
Write-Color "Backend desplegado en: https://$BackendUrl" "Green"

# 9. Build & Push Frontend (Con URL de Backend inyectada)
Write-Color "Construyendo y subiendo imagen Frontend (con VITE_API_URL)..." "Cyan"
Push-Location frontend
# Pasamos VITE_API_URL como build-arg
az acr build --registry $AcrName --image frontend:latest . --no-logs --build-arg "VITE_API_URL=https://$BackendUrl"
if ($LASTEXITCODE -ne 0) {
    Write-Color "Error construyendo imagen de Frontend." "Red"
    Pop-Location
    exit 1
}
Pop-Location

# 10. Desplegar Frontend
Write-Color "Desplegando Frontend..." "Cyan"
# Variables para frontend (Runtime env vars, aunque Vite usa build-time, es bueno tenerlas)
$FrontendEnvVars = @(
    "VITE_API_URL=https://$BackendUrl",
    "VITE_AZURE_AD_CLIENT_ID=$($BackendEnv['AZURE_AD_CLIENT_ID'])",
    "VITE_AZURE_AD_TENANT_ID=$($BackendEnv['AZURE_AD_TENANT_ID'])"
)

az containerapp create `
    --name $FrontendAppName `
    --resource-group $ResourceGroup `
    --environment $AcaEnv `
    --image "$AcrName.azurecr.io/frontend:latest" `
    --target-port 80 `
    --ingress external `
    --registry-server "$AcrName.azurecr.io" `
    --registry-username $AcrName `
    --registry-password $AcrPassword `
    --env-vars $FrontendEnvVars `
    --query properties.configuration.ingress.fqdn -o tsv

$FrontendUrl = az containerapp show --name $FrontendAppName --resource-group $ResourceGroup --query properties.configuration.ingress.fqdn -o tsv

Write-Color "--------------------------------------------------" "Green"
Write-Color "¡Despliegue Completado!" "Green"
Write-Color "Frontend URL: https://$FrontendUrl" "Green"
Write-Color "Backend URL: https://$BackendUrl" "Green"
Write-Color "--------------------------------------------------" "Green"
