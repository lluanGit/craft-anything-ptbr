import os
import sys
import winreg
from pathlib import Path
import subprocess

target_exe = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Craft Anything\craft-anything.exe")
target_dir = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Craft Anything")
icon_path = r"C:\Program Files\Craft Anything\craft-anything.exe"

desktop_dir = Path(os.path.expandvars(r"%USERPROFILE%\Desktop"))
start_menu_dir = Path(os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"))

# PowerShell helper to create shortcut
def make_shortcut(lnk_path, target, workdir, icon):
    ps = f"""
$sh = (New-Object -ComObject WScript.Shell).CreateShortcut('{lnk_path}')
$sh.TargetPath = '{target}'
$sh.WorkingDirectory = '{workdir}'
$sh.Description = 'Craft Anything v0.3.0 em Portugues (Brasil)'
$sh.IconLocation = '{icon},0'
$sh.Save()
"""
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)

# 1. Desktop shortcuts
for name in ["Craft Anything.lnk", "Craft Anything (PT-BR).lnk"]:
    p = desktop_dir / name
    make_shortcut(str(p), target_exe, target_dir, icon_path)
    print(f"[OK] Criado atalho na Area de Trabalho: {p}")

# 2. Start Menu shortcuts
for name in ["Craft Anything.lnk", "Craft Anything (PT-BR).lnk"]:
    p = start_menu_dir / name
    make_shortcut(str(p), target_exe, target_dir, icon_path)
    print(f"[OK] Criado atalho no Menu Iniciar: {p}")

# 3. HKCU App Paths
key_path = r"Software\Microsoft\Windows\CurrentVersion\App Paths\craft-anything.exe"
with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as k:
    winreg.SetValueEx(k, "", 0, winreg.REG_SZ, target_exe)
    winreg.SetValueEx(k, "Path", 0, winreg.REG_SZ, target_dir)
print(f"[OK] Registrado HKCU App Paths: {key_path} -> {target_exe}")
