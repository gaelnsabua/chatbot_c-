# ============================================================
# Script d'installation de MiKTeX (Distribution LaTeX)
# ============================================================

Write-Host "=== Installation de MiKTeX pour compiler des documents LaTeX ===" -ForegroundColor Cyan
Write-Host ""

# Vérifier si pdflatex est déjà installé
$pdflatexPaths = @(
    "pdflatex",
    "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe",
    "C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe"
)

$pdflatexFound = $false
foreach ($path in $pdflatexPaths) {
    try {
        if ($path -eq "pdflatex") {
            $result = Get-Command pdflatex -ErrorAction SilentlyContinue
            if ($result) {
                Write-Host "[OK] pdflatex est deja installe : $($result.Source)" -ForegroundColor Green
                $pdflatexFound = $true
                break
            }
        } elseif (Test-Path $path) {
            Write-Host "[OK] pdflatex trouve : $path" -ForegroundColor Green
            $pdflatexFound = $true
            
            # Ajouter au PATH si pas déjà présent
            $binDir = Split-Path $path -Parent
            if ($env:Path -notlike "*$binDir*") {
                Write-Host "[INFO] Ajout de MiKTeX au PATH de la session..." -ForegroundColor Yellow
                $env:Path += ";$binDir"
            }
            break
        }
    } catch {
        continue
    }
}

if ($pdflatexFound) {
    Write-Host ""
    Write-Host "MiKTeX est deja installe et fonctionnel !" -ForegroundColor Green
    Write-Host ""
    Write-Host "Vous pouvez compiler votre document avec :" -ForegroundColor Cyan
    Write-Host "  cd rapport" -ForegroundColor White
    Write-Host "  pdflatex main.tex" -ForegroundColor White
    Write-Host "  pdflatex main.tex  # 2e fois pour la table des matieres" -ForegroundColor White
    exit 0
}

# Si non trouvé, procéder à l'installation
Write-Host "[INFO] pdflatex n'est pas installe. Installation de MiKTeX..." -ForegroundColor Yellow
Write-Host ""

# URL de téléchargement de MiKTeX (installeur basique)
$miktexUrl = "https://miktex.org/download/ctan/systems/win32/miktex/setup/windows-x64/basic-miktex-24.1-x64.exe"
$installerPath = "$env:TEMP\miktex-setup.exe"

Write-Host "[1/4] Telechargement de MiKTeX (environ 200 Mo)..." -ForegroundColor Cyan
Write-Host "      URL: $miktexUrl" -ForegroundColor Gray

try {
    # Télécharger avec barre de progression
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $miktexUrl -OutFile $installerPath -UseBasicParsing
    $ProgressPreference = 'Continue'
    
    if (-not (Test-Path $installerPath)) {
        throw "Le telechargement a echoue"
    }
    
    $fileSize = (Get-Item $installerPath).Length / 1MB
    Write-Host "      Telechargement termine : $([math]::Round($fileSize, 2)) Mo" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] Echec du telechargement de MiKTeX" -ForegroundColor Red
    Write-Host "Erreur : $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Solutions alternatives :" -ForegroundColor Yellow
    Write-Host "1. Telechargement manuel depuis : https://miktex.org/download" -ForegroundColor White
    Write-Host "2. Utiliser Overleaf (en ligne) : https://www.overleaf.com/" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "[2/4] Installation de MiKTeX..." -ForegroundColor Cyan
Write-Host "      Cela peut prendre 5-10 minutes..." -ForegroundColor Gray
Write-Host "      Mode : Installation silencieuse pour l'utilisateur actuel" -ForegroundColor Gray
Write-Host ""

try {
    # Installation silencieuse pour l'utilisateur actuel
    # Options :
    #   --unattended : mode silencieux
    #   --auto-install=yes : installer automatiquement les packages manquants
    #   --shared=no : installer pour l'utilisateur seulement (pas besoin admin)
    $installArgs = @(
        "--unattended",
        "--auto-install=yes",
        "--shared=no"
    )
    
    $process = Start-Process -FilePath $installerPath -ArgumentList $installArgs -Wait -PassThru -NoNewWindow
    
    if ($process.ExitCode -ne 0) {
        throw "L'installation a retourne le code d'erreur $($process.ExitCode)"
    }
    
    Write-Host "      Installation terminee !" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] Echec de l'installation de MiKTeX" -ForegroundColor Red
    Write-Host "Erreur : $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Essayez une installation manuelle :" -ForegroundColor Yellow
    Write-Host "1. Ouvrez : $installerPath" -ForegroundColor White
    Write-Host "2. Suivez l'assistant d'installation" -ForegroundColor White
    Write-Host "3. Choisissez 'Install for current user only'" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "[3/4] Verification de l'installation..." -ForegroundColor Cyan

# Attendre quelques secondes pour que l'installation se finalise
Start-Sleep -Seconds 3

# Chemins possibles de MiKTeX
$possiblePaths = @(
    "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe",
    "C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe"
)

$installed = $false
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        Write-Host "      pdflatex trouve : $path" -ForegroundColor Green
        $installed = $true
        
        # Ajouter au PATH de la session
        $binDir = Split-Path $path -Parent
        $env:Path += ";$binDir"
        Write-Host "      Ajoute au PATH de la session" -ForegroundColor Green
        break
    }
}

if (-not $installed) {
    Write-Host "[ATTENTION] pdflatex non trouve apres installation" -ForegroundColor Yellow
    Write-Host "Vous devrez peut-etre redemarrer PowerShell ou votre ordinateur" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/4] Nettoyage..." -ForegroundColor Cyan

# Supprimer l'installeur téléchargé
if (Test-Path $installerPath) {
    Remove-Item $installerPath -Force
    Write-Host "      Fichier d'installation supprime" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Installation de MiKTeX terminee !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

if ($installed) {
    Write-Host "Vous pouvez maintenant compiler votre document LaTeX :" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  cd rapport" -ForegroundColor White
    Write-Host "  pdflatex main.tex" -ForegroundColor White
    Write-Host "  pdflatex main.tex  # 2e fois pour la table des matieres" -ForegroundColor White
    Write-Host ""
    Write-Host "Note : Au premier lancement, MiKTeX telecharge automatiquement" -ForegroundColor Yellow
    Write-Host "       les packages LaTeX manquants (peut prendre quelques minutes)" -ForegroundColor Yellow
} else {
    Write-Host "IMPORTANT : Redemarrez PowerShell et reessayez 'pdflatex main.tex'" -ForegroundColor Yellow
    Write-Host "Si le probleme persiste, ajoutez manuellement MiKTeX au PATH :" -ForegroundColor Yellow
    Write-Host "  C:\Users\$env:USERNAME\AppData\Local\Programs\MiKTeX\miktex\bin\x64" -ForegroundColor White
}

Write-Host ""
