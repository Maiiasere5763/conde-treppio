# Script de Sincronizacao Tripla do Banco de Dados da Skill Conde (Treppio V8.1)
param(
    [string]$CommitMessage = "chore(treppio): sincronizacao automatica do corpus e sandbox Conde"
)

$ErrorActionPreference = 'Continue'
$SourceDir = "D:\Conde_Treppio"
$GitExe = if (Test-Path "D:\Outros\Git\cmd\git.exe") { "D:\Outros\Git\cmd\git.exe" } else { "git" }

Write-Host "=== [1/3] Sincronizando com pastas em nuvem (OneDrive & Google Drive) ===" -ForegroundColor Cyan

$CloudTargets = @(
    "D:\One Drive\OneDrive - UNIOESTE\Conde_Treppio",
    "C:\Users\Usuário\OneDrive\Conde_Treppio"
)

# Detecta automaticamente unidades ou pastas do Google Drive (G:\Meu Drive, G:\My Drive, etc.)
Get-PSDrive -PSProvider FileSystem | ForEach-Object {
    $driveRoot = $_.Root
    if (Test-Path "${driveRoot}Meu Drive") {
        $CloudTargets += "${driveRoot}Meu Drive\Conde_Treppio"
    }
    if (Test-Path "${driveRoot}My Drive") {
        $CloudTargets += "${driveRoot}My Drive\Conde_Treppio"
    }
}

foreach ($target in $CloudTargets) {
    $parent = Split-Path -Parent $target
    if (Test-Path $parent) {
        New-Item -ItemType Directory -Force -Path $target | Out-Null
        robocopy $SourceDir $target /MIR /XD ".git" "__pycache__" /NFL /NDL /NJH /NJS | Out-Null
        Write-Host " -> Espelhado com sucesso em: $target" -ForegroundColor Green
    }
}

Write-Host "=== [2/3] Sincronizando com diretorios locais do Antigravity ===" -ForegroundColor Cyan
$LocalSkillDirs = @(
    "C:\Users\Usuário\.gemini\config\skills\conde",
    "C:\Users\Usuário\.gemini\skills\conde"
)
foreach ($skillDir in $LocalSkillDirs) {
    if (Test-Path $skillDir) {
        $item = Get-Item $skillDir -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            Write-Host " -> Juncao simbolica ativa em: $skillDir -> $SourceDir" -ForegroundColor Green
        } else {
            robocopy $SourceDir $skillDir /MIR /XD ".git" "__pycache__" /NFL /NDL /NJH /NJS | Out-Null
            Write-Host " -> Sincronizado em: $skillDir" -ForegroundColor Green
        }
    }
}

Write-Host "=== [3/3] Versionamento Git / GitHub em D:\Conde_Treppio ===" -ForegroundColor Cyan
Push-Location $SourceDir
if (Test-Path ".git") {
    & $GitExe add -A
    $status = & $GitExe status --porcelain
    if ($status) {
        & $GitExe commit -m $CommitMessage
        Write-Host " -> Novo commit registrado localmente." -ForegroundColor Green
    } else {
        Write-Host " -> Nenhuma alteracao pendente para commit." -ForegroundColor Yellow
    }
    $remotes = & $GitExe remote
    if ($remotes -contains "origin") {
        & $GitExe push -u origin main
        Write-Host " -> Enviado para o GitHub (origin/main)." -ForegroundColor Green
    } else {
        Write-Host " -> Repositorio Git local atualizado (adicione um remote origin ou autentique no gh CLI para push remoto)." -ForegroundColor Yellow
    }
}
Pop-Location
Write-Host "=== Sincronizacao Concluida! ===" -ForegroundColor Cyan
