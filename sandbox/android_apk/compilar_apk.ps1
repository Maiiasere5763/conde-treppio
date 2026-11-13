# ==============================================================================
# compilar_apk.ps1
# Compilador e Empacotador do Aplicativo Android (Codice_Treppio_Conde.apk)
# Integração da Matriz Quadripartite e Léxico /conde V8.5
# ==============================================================================
param(
    [switch]$SkipSync
)

$ErrorActionPreference = "Stop"

$RootDir = "D:\Conde_Treppio"
$SandboxDir = Join-Path $RootDir "sandbox"
$AndroidDir = Join-Path $SandboxDir "android_apk"
$DistDir = Join-Path $RootDir "dist"

New-Item -ItemType Directory -Force -Path $DistDir | Out-Null

Write-Host "=== [1/4] Atualizando Base Filológica e Sincronizando Assets Android ===" -ForegroundColor Cyan
python (Join-Path $SandboxDir "gerador_dicionario_integral_sandbox.py")
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao executar gerador_dicionario_integral_sandbox.py (exit $LASTEXITCODE)"
}

Write-Host "=== [2/4] Verificando Ambiente Java JDK e Android SDK ===" -ForegroundColor Cyan

# 1. Localizar ou Configurar JAVA_HOME
$JavaCandidates = @(
    $env:JAVA_HOME,
    "D:\Outros\Java",
    "C:\Program Files\Eclipse Adoptium\jdk-17*",
    "C:\Program Files\Microsoft\jdk-17*",
    "C:\Program Files\Java\jdk*"
)

$FoundJava = $null
foreach ($cand in $JavaCandidates) {
    if ($cand) {
        $resolved = Get-Item $cand -ErrorAction SilentlyContinue | Select-Object -Last 1
        if ($resolved -and (Test-Path (Join-Path $resolved.FullName "bin\java.exe"))) {
            $FoundJava = $resolved.FullName
            break
        }
    }
}

if (-not $FoundJava) {
    $javaCmd = Get-Command java -ErrorAction SilentlyContinue
    if ($javaCmd) {
        $javaBin = Split-Path -Parent $javaCmd.Source
        $FoundJava = Split-Path -Parent $javaBin
    }
}

if ($FoundJava) {
    $env:JAVA_HOME = $FoundJava
    Write-Host " -> Java JDK detectado em: $env:JAVA_HOME" -ForegroundColor Green
} else {
    Write-Host " -> Java JDK 17 nao localizado automaticamente no PATH." -ForegroundColor Yellow
    Write-Host "    Para compilar localmente no Windows, instale o OpenJDK 17 via:" -ForegroundColor Yellow
    Write-Host "    winget install Microsoft.OpenJDK.17" -ForegroundColor Yellow
}

# 2. Localizar Android SDK
$SdkCandidates = @(
    $env:ANDROID_HOME,
    $env:ANDROID_SDK_ROOT,
    "D:\Outros\AndroidSDK",
    "$env:LOCALAPPDATA\Android\Sdk"
)

$FoundSdk = $null
foreach ($cand in $SdkCandidates) {
    if ($cand -and (Test-Path $cand)) {
        $FoundSdk = (Get-Item $cand).FullName
        break
    }
}

if ($FoundSdk) {
    $env:ANDROID_HOME = $FoundSdk
    $env:ANDROID_SDK_ROOT = $FoundSdk
    Write-Host " -> Android SDK detectado em: $env:ANDROID_HOME" -ForegroundColor Green
} else {
    Write-Host " -> Android SDK nao configurado localmente." -ForegroundColor Yellow
}

Write-Host "=== [3/4] Compilando APK via Gradle Wrapper ===" -ForegroundColor Cyan
Push-Location $AndroidDir

$BuildSuccess = $false
$ApkBuiltPath = $null

if ($FoundJava -and $FoundSdk) {
    & .\gradlew.bat assembleRelease --no-daemon
    if ($LASTEXITCODE -eq 0) {
        $ApkBuiltPath = Get-ChildItem "app\build\outputs\apk" -Filter "*.apk" -Recurse | Select-Object -Last 1 -ExpandProperty FullName
        if ($ApkBuiltPath) {
            $BuildSuccess = $true
        }
    }
}

Pop-Location

Write-Host "=== [4/4] Finalizacao e Disponibilizacao do APK ===" -ForegroundColor Cyan
$DestApk = Join-Path $DistDir "Codice_Treppio_Conde.apk"
$RootApk = Join-Path $RootDir "Codice_Treppio_Conde.apk"

if ($BuildSuccess -and $ApkBuiltPath) {
    Copy-Item -Path $ApkBuiltPath -Destination $DestApk -Force
    Copy-Item -Path $ApkBuiltPath -Destination $RootApk -Force
    Write-Host " -> APK compilado com sucesso localmente: $DestApk ($((Get-Item $DestApk).Length) bytes)" -ForegroundColor Green
} else {
    Write-Host " -> Falha na compilacao local do APK (verifique JDK 17 e Android SDK)." -ForegroundColor Red
    exit 1
}

if (-not $SkipSync) {
    powershell -ExecutionPolicy Bypass -File (Join-Path $RootDir "sync_conde.ps1") -CommitMessage "chore(android): atualizacao dos assets do APK e configuracoes Gradle"
    if ($LASTEXITCODE -ne 0) {
        throw "sync_conde.ps1 falhou com codigo $LASTEXITCODE"
    }
}

