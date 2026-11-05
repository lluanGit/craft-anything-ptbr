<#
.SYNOPSIS
    Desinstalador do Plugin de Localizacao PT-BR para o Craft Anything (T5.2).
#>

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Desinstalando o plugin Craft Anything PT-BR..." -ForegroundColor Yellow

# 1. Restaurar backup em C:\Program Files\Craft Anything se existir
$SourceExe = "C:\Program Files\Craft Anything\craft-anything.exe"
$BackupExe = "$SourceExe.bak"
if (Test-Path $BackupExe) {
    try {
        Copy-Item -Path $BackupExe -Destination $SourceExe -Force
        Remove-Item -Path $BackupExe -Force
        Write-Host "[OK] Binario original restaurado em $SourceExe" -ForegroundColor Green
    } catch {
        Write-Host "[AVISO] Execute como Administrador para restaurar $SourceExe." -ForegroundColor Yellow
    }
}

# 2. Remover instalacao local em %LOCALAPPDATA%\Programs\Craft Anything
$LocalInstallDir = Join-Path $env:LOCALAPPDATA "Programs\Craft Anything"
if (Test-Path $LocalInstallDir) {
    Remove-Item -Path $LocalInstallDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Diretorio local removido: $LocalInstallDir" -ForegroundColor Green
}

# 3. Restaurar idioma padrao em %APPDATA%\craft-anything\config.toml
$ConfigFile = Join-Path $env:APPDATA "craft-anything\config.toml"
if (Test-Path $ConfigFile) {
    $RawConfig = Get-Content -Path $ConfigFile -Raw -Encoding UTF8
    $RawConfig = [regex]::Replace($RawConfig, '(?m)^language\s*=\s*"pt[^"]*"\r?\n?', '')
    $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($ConfigFile, $RawConfig, $Utf8NoBom)
    Write-Host "[OK] Configuracao de idioma removida de $ConfigFile" -ForegroundColor Green
}

# 4. Remover chave HKCU App Paths e atalhos
$AppPathsKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\App Paths\craft-anything.exe"
if (Test-Path $AppPathsKey) {
    Remove-Item -Path $AppPathsKey -Force
}
$StartShortcut = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Craft Anything (PT-BR).lnk"
if (Test-Path $StartShortcut) {
    Remove-Item -Path $StartShortcut -Force
}
$DesktopPath = [Environment]::GetFolderPath("Desktop")
foreach ($f in @("Craft Anything (PT-BR).lnk", "Atualizar Craft Anything para PT-BR.bat")) {
    $target = Join-Path $DesktopPath $f
    if (Test-Path $target) {
        Remove-Item -Path $target -Force
    }
}

Write-Host "[OK] Desinstalacao concluida com sucesso!" -ForegroundColor Green
