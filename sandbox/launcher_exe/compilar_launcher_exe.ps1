# ==============================================================================
# compilar_launcher_exe.ps1
# Compila o Executável Portátil Nativo (Codice_Treppio_Conde.exe) embutindo a UI
# e as 37.769 formas do banco de dados do /conde como recursos internos.
# ==============================================================================
$ErrorActionPreference = "Stop"

$RootDir = "D:\Conde_Treppio"
$SandboxDir = Join-Path $RootDir "sandbox"
$LauncherDir = Join-Path $SandboxDir "launcher_exe"
$DistDir = Join-Path $RootDir "dist"

New-Item -ItemType Directory -Force -Path $DistDir | Out-Null

Write-Host "=== [1/3] Atualizando Banco de Dados, GitHub Pages (docs/) e Pacote Web Portatil ===" -ForegroundColor Cyan
python (Join-Path $SandboxDir "gerador_dicionario_integral_sandbox.py")

$CscPath = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if (-not (Test-Path $CscPath)) {
    $CscPath = (Get-ChildItem "C:\Windows\Microsoft.NET\Framework*\*\csc.exe" | Select-Object -Last 1).FullName
}

$CsSource = Join-Path $LauncherDir "LauncherConde.cs"
$HtmlRes = Join-Path $SandboxDir "ui_dicionario\index.html"
$JsonRes = Join-Path $SandboxDir "dicionario_exaustivo\dicionario_formas_expandidas.json"
$OutExe = Join-Path $DistDir "Codice_Treppio_Conde.exe"
$RootExe = Join-Path $RootDir "Codice_Treppio_Conde.exe"

Write-Host "=== [2/3] Compilando Executavel Nativo Windows (Codice_Treppio_Conde.exe) ===" -ForegroundColor Cyan
& $CscPath `
    /nologo `
    /target:winexe `
    /optimize+ `
    "/out:$OutExe" `
    "/resource:$HtmlRes,index.html" `
    "/resource:$JsonRes,dicionario_formas_expandidas.json" `
    /r:System.dll `
    /r:System.Drawing.dll `
    /r:System.Windows.Forms.dll `
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
