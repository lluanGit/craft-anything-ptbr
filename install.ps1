<#
.SYNOPSIS
    Instalador Automatizado do Plugin de Localizacao PT-BR para o Craft Anything v0.3.0 (T5.2).

.DESCRIPTION
    1. Valida o catalogo de traducao (1.363 chaves em locales/pt-BR.tsv).
    2. Gera o executavel localizado em Portugues (Brasil) em:
       - %LOCALAPPDATA%\Programs\Craft Anything\craft-anything.exe (sem necessidade de Admin)
       - E atualiza C:\Program Files\Craft Anything\craft-anything.exe (com backup .bak) caso executado como Administrador.
    3. Compila o launcher nativo CraftAnything-PTBR.exe.
    4. Atualiza %APPDATA%\craft-anything\config.toml com `language = "pt-BR"` e registra o servidor MCP `craft-anything-ptbr`.
    5. Registra o caminho no registro do usuario (HKCU App Paths) e cria atalhos no Menu Iniciar.
#>

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PyCmd = Get-Command python -ErrorAction SilentlyContinue
if ($PyCmd) {
    $PythonExe = $PyCmd.Source
} else {
    $PyCandidate = Get-ChildItem -Path "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe" -ErrorAction SilentlyContinue | Select-Object -Last 1
    if ($PyCandidate) {
        $PythonExe = $PyCandidate.FullName
    } else {
        throw "Python 3 nao encontrado. Instale o Python 3 e tente novamente."
    }
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Craft Anything PT-BR Plugin - Instalador v1.0.0" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Validar catalogo com linter
Write-Host "`n[1/5] Validando catalogo de traducao (1.363 chaves)..." -ForegroundColor Yellow
& $PythonExe "$ProjectRoot\scripts\lint_catalog.py" --tsv "$ProjectRoot\locales\pt-BR.tsv" --keys "$ProjectRoot\locales\catalog_keys.json"
if ($LASTEXITCODE -ne 0) {
    throw "Falha na validacao do catalogo PT-BR."
}

# 2. Gerar binarios localizados em %LOCALAPPDATA%\Programs\Craft Anything
$SourceDir = "C:\Program Files\Craft Anything"
$SourceExe = Join-Path $SourceDir "craft-anything.exe"
$LocalInstallDir = Join-Path $env:LOCALAPPDATA "Programs\Craft Anything"
$LocalExe = Join-Path $LocalInstallDir "craft-anything.exe"

Write-Host "`n[2/5] Construindo pacote localizado em '$LocalInstallDir'..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $LocalInstallDir | Out-Null

# Copiar arquivos auxiliares da instalacao original (ex: craft-anything-cli.exe, DLLs se houver)
Get-ChildItem -Path $SourceDir -File | Where-Object { $_.Name -ne "craft-anything.exe" } | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination (Join-Path $LocalInstallDir $_.Name) -Force
}

& $PythonExe "$ProjectRoot\src\plugin_patcher.py" --source "$SourceExe" --target "$LocalExe" --catalog "$ProjectRoot\locales\pt-BR.tsv"
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao aplicar o patch de localizacao no executavel."
}

# Se estiver rodando como Administrador (ou tiver permissao de escrita em C:\Program Files\Craft Anything), aplica in-place com backup
$BackupExe = "$SourceExe.bak"
try {
    if (-not (Test-Path $BackupExe)) {
        Copy-Item -Path $SourceExe -Destination $BackupExe -Force -ErrorAction Stop
    }
    Copy-Item -Path $LocalExe -Destination $SourceExe -Force -ErrorAction Stop
    Write-Host "[OK] Binario principal em '$SourceExe' atualizado in-place (backup salvo em craft-anything.exe.bak)." -ForegroundColor Green
} catch {
    Write-Host "[INFO] Instalacao em modo Usuario (sem elevacao UAC): binario PT-BR instalado em '$LocalExe'." -ForegroundColor Gray
}

# 3. Compilar Launcher Nativo CraftAnything-PTBR.exe
Write-Host "`n[3/5] Compilando loader nativo CraftAnything-PTBR.exe..." -ForegroundColor Yellow
$CscExe = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$LoaderOut = Join-Path $LocalInstallDir "CraftAnything-PTBR.exe"
if (Test-Path $CscExe) {
    & $CscExe /nologo /target:winexe /optimize+ "/out:$LoaderOut" "$ProjectRoot\src\CraftAnythingPTBRLoader.cs"
    Copy-Item -Path $LoaderOut -Destination (Join-Path $ProjectRoot "CraftAnything-PTBR.exe") -Force
    Write-Host "[OK] Loader compilado em: $LoaderOut" -ForegroundColor Green
}

# 4. Configurar %APPDATA%\craft-anything\config.toml (language = "pt-BR" + MCP Plugin)
Write-Host "`n[4/5] Configurando idioma 'pt-BR' e servidor MCP em config.toml..." -ForegroundColor Yellow
$ConfigDir = Join-Path $env:APPDATA "craft-anything"
$ConfigFile = Join-Path $ConfigDir "config.toml"
New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null

$McpServerPath = (Join-Path $ProjectRoot "src\mcp_server.py").Replace("\", "\\")
$PythonPathEscaped = $PythonExe.Replace("\", "\\")

if (Test-Path $ConfigFile) {
    $RawConfig = Get-Content -Path $ConfigFile -Raw -Encoding UTF8
    if ($RawConfig -match '(?m)^language\s*=') {
        $RawConfig = [regex]::Replace($RawConfig, '(?m)^language\s*=\s*"[^"]*"', 'language = "pt-BR"')
    } else {
        $RawConfig = "language = `"pt-BR`"`r`n" + $RawConfig
    }
} else {
    $RawConfig = "language = `"pt-BR`"`r`n"
}

if ($RawConfig -notmatch 'craft-anything-ptbr') {
    $RawConfig = [regex]::Replace($RawConfig, '(?m)^mcp\s*=\s*\[\s*\]\r?\n?', '')
    $McpBlock = @"

[[plugins.mcp]]
id = "craft_anything_ptbr"
name = "craft-anything-ptbr"
transport = "stdio"
command = "$PythonPathEscaped"
args = ["$McpServerPath"]
enabled = true
"@
    $RawConfig = $RawConfig.TrimEnd() + "`r`n" + $McpBlock + "`r`n"
}

$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($ConfigFile, $RawConfig, $Utf8NoBom)
Write-Host "[OK] Arquivo '$ConfigFile' configurado com language = 'pt-BR' e plugin MCP 'craft-anything-ptbr'." -ForegroundColor Green

# 5. Registrar App Paths no HKCU e criar atalho no Menu Iniciar do usuario
Write-Host "`n[5/5] Registrando atalhos do usuario e HKCU App Paths..." -ForegroundColor Yellow
$AppPathsKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\App Paths\craft-anything.exe"
New-Item -Path $AppPathsKey -Force | Out-Null
Set-ItemProperty -Path $AppPathsKey -Name "(Default)" -Value $LocalExe
Set-ItemProperty -Path $AppPathsKey -Name "Path" -Value $LocalInstallDir

$StartMenuDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$ShortcutPath = Join-Path $StartMenuDir "Craft Anything (PT-BR).lnk"
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $LocalExe
$Shortcut.WorkingDirectory = $LocalInstallDir
$Shortcut.Description = "Craft Anything v0.3.0 em Portugues (Brasil)"
$Shortcut.IconLocation = "$SourceExe,0"
$Shortcut.Save()

$DesktopDir = [Environment]::GetFolderPath("Desktop")
if ($DesktopDir -and (Test-Path $DesktopDir)) {
    $DeskShortcutPath = Join-Path $DesktopDir "Craft Anything (PT-BR).lnk"
    $DeskShortcut = $WshShell.CreateShortcut($DeskShortcutPath)
    $DeskShortcut.TargetPath = $LocalExe
    $DeskShortcut.WorkingDirectory = $LocalInstallDir
    $DeskShortcut.Description = "Craft Anything v0.3.0 em Portugues (Brasil)"
    $DeskShortcut.IconLocation = "$SourceExe,0"
    $DeskShortcut.Save()
}

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "  Instalacao do Plugin PT-BR concluida com sucesso!" -ForegroundColor Green
Write-Host "  - Idioma ativo: Portugues (Brasil) (pt-BR)" -ForegroundColor Green
Write-Host "  - Executavel PT-BR: $LocalExe" -ForegroundColor Green
Write-Host "  - Atalho Menu Iniciar: $ShortcutPath" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
