# ==============================================================================
# compilar_launcher_exe.ps1
# Compila o Executável Portátil Nativo (Codice_Treppio_Conde.exe) embutindo a UI,
# o Brasão do Conde e o banco comprimido em GZip como recursos internos (V8.5).
# ==============================================================================
param(
    [switch]$SkipGen
)

$ErrorActionPreference = "Stop"

$RootDir = "D:\Conde_Treppio"
$SandboxDir = Join-Path $RootDir "sandbox"
$LauncherDir = Join-Path $SandboxDir "launcher_exe"
$UiDir = Join-Path $SandboxDir "ui_dicionario"
$DistDir = Join-Path $RootDir "dist"

New-Item -ItemType Directory -Force -Path $DistDir | Out-Null

if (-not $SkipGen) {
    Write-Host "=== [1/3] Atualizando Banco de Dados, GitHub Pages (docs/), APK e Brasao ===" -ForegroundColor Cyan
    python (Join-Path $SandboxDir "gerador_dicionario_integral_sandbox.py")
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao executar gerador_dicionario_integral_sandbox.py (codigo $LASTEXITCODE)"
    }
}

$CscPath = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if (-not (Test-Path $CscPath)) {
    $CscPath = (Get-ChildItem "C:\Windows\Microsoft.NET\Framework*\*\csc.exe" | Select-Object -Last 1).FullName
}

$CsSource = Join-Path $LauncherDir "LauncherConde.cs"
$HtmlRes = Join-Path $UiDir "index.html"
$JsonGzRes = Join-Path $SandboxDir "dicionario_exaustivo\dicionario_formas_expandidas.compact.json.gz"
$JsonRawRes = Join-Path $SandboxDir "dicionario_exaustivo\dicionario_formas_expandidas.json"

if (-not (Test-Path $JsonGzRes)) {
    if (-not (Test-Path $JsonRawRes)) {
        throw "Arquivo de dados nao encontrado: $JsonRawRes"
    }
    $rawBytes = [System.IO.File]::ReadAllBytes($JsonRawRes)
    $fs = [System.IO.File]::Create($JsonGzRes)
    $gz = New-Object System.IO.Compression.GzipStream($fs, [System.IO.Compression.CompressionLevel]::Optimal)
    $gz.Write($rawBytes, 0, $rawBytes.Length)
    $gz.Dispose()
    $fs.Dispose()
}

$Win32Icon = Join-Path $LauncherDir "conde_brasao.ico"
$FormGdiIco = Join-Path $LauncherDir "conde_form_gdi.ico"
$CrestPng = Join-Path $LauncherDir "conde_crest_header.png"
$ManifestRes = Join-Path $UiDir "manifest.json"
$SwRes = Join-Path $UiDir "sw.js"
$Icon512Res = Join-Path $UiDir "icon-512.png"
$Icon192Res = Join-Path $UiDir "icon-192.png"
$IconMaskRes = Join-Path $UiDir "icon-maskable-512.png"
$FaviconRes = Join-Path $UiDir "favicon.ico"

$OutExe = Join-Path $DistDir "Codice_Treppio_Conde.exe"
$RootExe = Join-Path $RootDir "Codice_Treppio_Conde.exe"

$SpeechDll = Get-ChildItem "C:\Windows\Microsoft.NET\assembly\GAC_MSIL\System.Speech" -Recurse -Filter "System.Speech.dll" -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
$RefArgs = @(
    "/r:System.dll",
    "/r:System.Core.dll",
    "/r:System.Drawing.dll",
    "/r:System.Windows.Forms.dll"
)
if ($SpeechDll -and (Test-Path $SpeechDll)) {
    $RefArgs += "/r:$SpeechDll"
}

$ResArgs = @(
    "/resource:$HtmlRes,index.html",
    "/resource:$JsonGzRes,dicionario_formas_expandidas.json.gz"
)
$OptRes = @{
    "manifest.json"          = $ManifestRes
    "sw.js"                  = $SwRes
    "icon-512.png"           = $Icon512Res
    "icon-192.png"           = $Icon192Res
    "icon-maskable-512.png"  = $IconMaskRes
    "favicon.ico"            = $FaviconRes
    "conde_form_gdi.ico"     = $FormGdiIco
    "conde_crest_header.png" = $CrestPng
    "brasao_conde.svg"       = (Join-Path $UiDir "brasao_conde.svg")
}
foreach ($k in $OptRes.Keys) {
    $p = $OptRes[$k]
    if (Test-Path $p) {
        $ResArgs += "/resource:$p,$k"
    }
}

$IconArgs = @()
if (Test-Path $Win32Icon) {
    $IconArgs += "/win32icon:$Win32Icon"
}

Write-Host "=== [2/3] Compilando Executavel Nativo Windows (Codice_Treppio_Conde.exe) ===" -ForegroundColor Cyan
& $CscPath `
    /nologo `
    /target:winexe `
    /optimize+ `
    @IconArgs `
    "/out:$OutExe" `
    @ResArgs `
    @RefArgs `
    $CsSource

if ($LASTEXITCODE -ne 0) {
    throw "Falha na compilacao C# (codigo $LASTEXITCODE)"
}

Copy-Item -Path $OutExe -Destination $RootExe -Force

Write-Host " -> Executavel gerado com sucesso: $OutExe ($((Get-Item $OutExe).Length) bytes)" -ForegroundColor Green
Write-Host " -> Copia na raiz:                 $RootExe" -ForegroundColor Green

Write-Host "=== [3/3] Executando Auto-Teste Headless do Executavel ===" -ForegroundColor Cyan
$proc = Start-Process -FilePath $OutExe -ArgumentList "--test-headless" -Wait -PassThru
Write-Host " -> ExitCode: $($proc.ExitCode)" -ForegroundColor Green
if (Test-Path (Join-Path $DistDir "headless_test_result.txt")) {
    Get-Content (Join-Path $DistDir "headless_test_result.txt")
    Remove-Item (Join-Path $DistDir "headless_test_result.txt") -Force
}
if ($proc.ExitCode -ne 0) {
    throw "Auto-teste headless falhou com codigo $($proc.ExitCode)"
}
