@echo off
title Conversacao por Voz - Antigravity e O Conde
cd /d "D:\Conde_Treppio\sandbox"
start "" pythonw "D:\Conde_Treppio\sandbox\interface_voz_whisper.py"
if errorlevel 1 (
    python "D:\Conde_Treppio\sandbox\interface_voz_whisper.py"
    pause
)
