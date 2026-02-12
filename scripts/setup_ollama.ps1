# SQUAD-CSHARP - Installation Ollama (Windows PowerShell)
# Exécution: .\scripts\setup_ollama.ps1

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SQUAD-CSHARP - Installation Ollama" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si Ollama est déjà installé (plusieurs emplacements possibles)
$ollamaExe = $null

# 1. Chercher dans le PATH
$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
if ($ollamaCmd) {
    $ollamaExe = $ollamaCmd.Source
}

# 2. Emplacements courants sur Windows
if (-not $ollamaExe) {
    $possiblePaths = @(
        "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe",
        "$env:LOCALAPPDATA\Ollama\ollama.exe",
        "$env:PROGRAMFILES\Ollama\ollama.exe",
        "$env:USERPROFILE\AppData\Local\Programs\Ollama\ollama.exe",
        "C:\Program Files\Ollama\ollama.exe"
    )
    foreach ($p in $possiblePaths) {
        if (Test-Path $p) {
            $ollamaExe = $p
            break
        }
    }
}

# 3. Chercher via le registre (installation Windows)
if (-not $ollamaExe) {
    $regPath = Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*" -ErrorAction SilentlyContinue |
        Where-Object { $_.DisplayName -like "*Ollama*" } |
        Select-Object -First 1 -ExpandProperty InstallLocation -ErrorAction SilentlyContinue
    if ($regPath -and (Test-Path "$regPath\ollama.exe")) {
        $ollamaExe = "$regPath\ollama.exe"
    }
}

if ($ollamaExe) {
    Write-Host "[OK] Ollama trouvé : $ollamaExe" -ForegroundColor Green
    # Ajouter au PATH de la session si besoin
    $ollamaDir = Split-Path $ollamaExe -Parent
    if ($env:PATH -notlike "*$ollamaDir*") {
        $env:PATH = "$ollamaDir;$env:PATH"
        Write-Host "[INFO] Ollama ajouté au PATH de la session" -ForegroundColor Yellow
    }
} else {
    Write-Host "[INFO] Ollama n'est pas détecté sur cette machine." -ForegroundColor Yellow
    Write-Host "[INFO] Téléchargez-le depuis : https://ollama.ai/download" -ForegroundColor Yellow
    Write-Host ""
    
    $install = Read-Host "Voulez-vous ouvrir la page de téléchargement ? (O/N)"
    if ($install -eq "O" -or $install -eq "o") {
        Start-Process "https://ollama.ai/download"
        Write-Host "[INFO] Installez Ollama puis relancez ce script." -ForegroundColor Yellow
        exit
    }
}

Write-Host ""

# Vérifier qu'Ollama fonctionne
Write-Host "[...] Vérification du serveur Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 5
    Write-Host "[OK] Serveur Ollama accessible" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Serveur Ollama non accessible. Démarrage..." -ForegroundColor Yellow
    Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

# Télécharger le modèle de base
Write-Host ""
Write-Host "[...] Téléchargement du modèle llama3.2:3b..." -ForegroundColor Yellow
Write-Host "[INFO] Cela peut prendre quelques minutes selon votre connexion." -ForegroundColor Yellow
ollama pull llama3.2:3b

# Créer le modèle SQUAD-CSHARP
Write-Host ""
Write-Host "[...] Création du modèle SQUAD-CSHARP..." -ForegroundColor Yellow
$modelfilePath = Join-Path $PSScriptRoot "..\models\Modelfile"
ollama create SQUAD-CSHARP -f $modelfilePath

# Vérification
Write-Host ""
Write-Host "[...] Vérification..." -ForegroundColor Yellow
ollama list

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Installation terminée !" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaine étape : python scripts/ingest_pdfs.py" -ForegroundColor Cyan
Write-Host ""
