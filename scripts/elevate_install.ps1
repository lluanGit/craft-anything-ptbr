param(
    [string]$SourceExe = "$env:LOCALAPPDATA\Programs\Craft Anything\craft-anything.exe",
    [string]$TargetExe = "C:\Program Files\Craft Anything\craft-anything.exe"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $SourceExe)) {
    throw "Source executable not found: $SourceExe"
}

$Bak = "$TargetExe.bak"
if (Test-Path $TargetExe) {
    if (-not (Test-Path $Bak)) {
        Copy-Item -Path $TargetExe -Destination $Bak -Force
    }
}

Copy-Item -Path $SourceExe -Destination $TargetExe -Force
Write-Host "C:\Program Files\Craft Anything\craft-anything.exe replaced successfully!"
