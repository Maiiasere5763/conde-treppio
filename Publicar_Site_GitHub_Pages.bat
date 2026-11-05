@echo off
chcp 65001 >nul
set GH_EXE=D:\Outros\GitHubCLI\gh.exe
set GIT_EXE=D:\Outros\Git\cmd\git.exe
cd /d D:\Conde_Treppio

echo ============================================================================
echo   Publicador Automatico do Dicionario Treppio (/conde) no GitHub Pages
echo ============================================================================
echo.
"%GH_EXE%" auth status >nul 2>&1
if errorlevel 1 (
    echo [1/3] Autenticando sua conta do GitHub no navegador...
    "%GH_EXE%" auth login --web -p https
)

echo [2/3] Sincronizando e enviando repositorio conde-treppio para o GitHub...
"%GH_EXE%" repo view conde-treppio >nul 2>&1
if errorlevel 1 (
    "%GH_EXE%" repo create conde-treppio --public --source=. --remote=origin --push
) else (
    "%GIT_EXE%" push -u origin main
)

echo [3/3] Ativando o site gratuito no GitHub Pages (pasta /docs)...
for /f "delims=" %%u in ('"%GH_EXE%" api user --jq .login') do set GH_USER=%%u
"%GH_EXE%" api -X POST "repos/%GH_USER%/conde-treppio/pages" -f "source[branch]=main" -f "source[path]=/docs" >nul 2>&1

echo.
echo ============================================================================
echo   PUBLICACAO CONCLUIDA!
echo   -> Site Publico para seus amigos: https://%GH_USER%.github.io/conde-treppio/
echo   -> Download do APK Android:       https://github.com/%GH_USER%/conde-treppio/releases
echo   -> URL do Banco JSON Online:      https://raw.githubusercontent.com/%GH_USER%/conde-treppio/main/docs/dicionario_formas_expandidas.json
echo ============================================================================
pause

