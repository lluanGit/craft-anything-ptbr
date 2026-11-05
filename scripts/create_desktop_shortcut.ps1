$ErrorActionPreference = "Stop"

$Desktop = [Environment]::GetFolderPath("Desktop")
$TargetExe = "$env:LOCALAPPDATA\Programs\Craft Anything\craft-anything.exe"
$WorkDir = "$env:LOCALAPPDATA\Programs\Craft Anything"
$IconPath = "C:\Program Files\Craft Anything\craft-anything.exe"

$WshShell = New-Object -ComObject WScript.Shell

# 1. Atalho na Area de Trabalho real do usuario
$LnkDesk = Join-Path $Desktop "Craft Anything (PT-BR).lnk"
$Shortcut = $WshShell.CreateShortcut($LnkDesk)
$Shortcut.TargetPath = $TargetExe
$Shortcut.WorkingDirectory = $WorkDir
$Shortcut.Description = "Craft Anything v0.3.0 em Portugues (Brasil)"
$Shortcut.IconLocation = "$IconPath,0"
$Shortcut.Save()
Write-Host "[OK] Atalho criado na Area de Trabalho: $LnkDesk"

# 2. Atalho no Menu Iniciar do usuario
$StartMenu = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
$LnkStart = Join-Path $StartMenu "Craft Anything (PT-BR).lnk"
$Shortcut2 = $WshShell.CreateShortcut($LnkStart)
$Shortcut2.TargetPath = $TargetExe
$Shortcut2.WorkingDirectory = $WorkDir
$Shortcut2.Description = "Craft Anything v0.3.0 em Portugues (Brasil)"
$Shortcut2.IconLocation = "$IconPath,0"
$Shortcut2.Save()
Write-Host "[OK] Atalho criado no Menu Iniciar: $LnkStart"
