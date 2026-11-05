@echo off
chcp 65001 >nul
echo ============================================================================
echo   Compilador do Aplicativo Android (Codice_Treppio_Conde.apk)
echo   Era Classica V8.1 (/conde)
echo ============================================================================
echo.
powershell -ExecutionPolicy Bypass -File "D:\Conde_Treppio\sandbox\android_apk\compilar_apk.ps1"
echo.
pause
