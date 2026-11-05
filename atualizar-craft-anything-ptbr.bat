@echo off
chcp 65001 >nul
title Atualizador Craft Anything PT-BR

echo ============================================================
echo   Atualizando Craft Anything para Portugues (Brasil)
echo ============================================================
echo.

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Solicitando permissao de Administrador (UAC)...
    powershell -NoProfile -Command "Start-Process cmd -ArgumentList '/c \"\"%~dpnx0\"\"' -Verb RunAs"
    exit /b
)

set "SOURCE=%LOCALAPPDATA%\Programs\Craft Anything\craft-anything.exe"
set "TARGET=C:\Program Files\Craft Anything\craft-anything.exe"
set "BACKUP=C:\Program Files\Craft Anything\craft-anything.exe.bak"

if not exist "%SOURCE%" (
    echo [ERRO] Binario PT-BR nao encontrado em:
    echo   %SOURCE%
    echo.
    pause
    exit /b 1
)

echo [1/2] Verificando backup original...
if not exist "%BACKUP%" (
    if exist "%TARGET%" (
        copy /y "%TARGET%" "%BACKUP%" >nul
        echo [OK] Backup salvo em: %BACKUP%
    )
) else (
    echo [INFO] Backup original ja existe.
)

echo [2/2] Atualizando executavel principal em Program Files...
copy /y "%SOURCE%" "%TARGET%" >nul
if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao substituir o executavel.
    echo Certifique-se de que o Craft Anything e o ArtCraft Launcher estejam FECHADOS.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  [SUCESSO] Craft Anything atualizado com sucesso!
echo ============================================================
echo  O aplicativo agora esta 100%% em Portugues (Brasil).
echo  Voce pode abrir normalmente pelo:
echo    - ArtCraft Launcher
echo    - Menu Iniciar
echo    - Atalho na Area de Trabalho: "Craft Anything (PT-BR)"
echo ============================================================
echo.
pause
