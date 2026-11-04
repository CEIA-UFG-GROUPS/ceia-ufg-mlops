#Requires -Version 5.1
<#
.SYNOPSIS
    Verificador de ambiente da Semana 00 (Windows / PowerShell).

.DESCRIPTION
    Checa, item a item, se o ambiente do grupo de estudos esta pronto: git,
    GitHub por SSH, python, docker, wsl, gcloud e (opcionalmente) o acesso a
    maquina 4090 do laboratorio. Cada item imprime OK ou FALHA, com uma dica
    de como resolver. Nenhum item e instalado ou alterado: o script so le.

.PARAMETER HostLab
    Host SSH da maquina do laboratorio, no formato usuario@servidor. Se nao for
    informado, o script usa a variavel de ambiente LAB_SSH_HOST. Sem nenhum dos
    dois, essa checagem e pulada.

.PARAMETER PularRede
    Pula as checagens que dependem de rede (SSH para o GitHub e para o lab).

.EXAMPLE
    .\verificar-ambiente.ps1

.EXAMPLE
    .\verificar-ambiente.ps1 -HostLab aluno@gpu01.lab.ufg.br
#>
[CmdletBinding()]
param(
    [string] $HostLab = $env:LAB_SSH_HOST,
    [switch] $PularRede
)

# Nao abortar no primeiro erro: a graca do verificador e listar TUDO que falta.
$ErrorActionPreference = 'Continue'

# O console precisa estar em UTF-8 para desenhar os simbolos abaixo.
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

# Definidos por codepoint de proposito: assim este arquivo continua ASCII puro e
# nao depende do PowerShell adivinhar a codificacao certa na hora de ler.
$OK    = [char]::ConvertFromUtf32(0x2705)  # marca verde
$FALHA = [char]::ConvertFromUtf32(0x274C)  # xis vermelho
$AVISO = [char]::ConvertFromUtf32(0x26A0)  # triangulo de atencao

$script:Falhas = 0
$script:Avisos = 0

function Write-Secao {
    param([string] $Titulo)
    Write-Host ''
    Write-Host "-- $Titulo " -ForegroundColor Cyan
}

function Write-Ok {
    param([string] $Rotulo, [string] $Detalhe)
    Write-Host "$OK $Rotulo" -NoNewline
    if ($Detalhe) { Write-Host "  $Detalhe" -ForegroundColor DarkGray } else { Write-Host '' }
}

function Write-Falha {
    param([string] $Rotulo, [string] $Dica)
    $script:Falhas++
    Write-Host "$FALHA $Rotulo" -ForegroundColor Red
    if ($Dica) { Write-Host "     -> $Dica" -ForegroundColor DarkGray }
}

function Write-Aviso {
    param([string] $Rotulo, [string] $Dica)
    $script:Avisos++
    Write-Host "$AVISO  $Rotulo" -ForegroundColor Yellow
    if ($Dica) { Write-Host "     -> $Dica" -ForegroundColor DarkGray }
}

function Test-Comando {
    param([string] $Nome)
    return $null -ne (Get-Command $Nome -ErrorAction SilentlyContinue)
}

function Get-SaidaComando {
    <#
        Executa um programa externo e devolve { Ok; Texto }, sem deixar o
        stderr virar um erro barulhento do PowerShell.
    #>
    param(
        [string]   $Exe,
        [string[]] $Argumentos = @()
    )

    # Atencao: NAO troque para 'SilentlyContinue'. No Windows PowerShell 5.1 isso
    # descarta o stderr do programa externo, e justamente ali que moram as
    # mensagens que interessam (o 'ssh -T git@github.com', por exemplo, responde
    # inteiramente por stderr). Como a saida vai para uma variavel, nada vaza
    # para a tela.
    $anterior = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $global:LASTEXITCODE = 0
        $bruto = & $Exe @Argumentos 2>&1
        $texto = (@($bruto) | ForEach-Object { "$_" }) -join "`n"
        return [pscustomobject]@{ Ok = ($LASTEXITCODE -eq 0); Texto = $texto.Trim() }
    }
    catch {
        return [pscustomobject]@{ Ok = $false; Texto = $_.Exception.Message }
    }
    finally {
        $ErrorActionPreference = $anterior
    }
}

function Test-Ferramenta {
    <# Checa "o comando existe e responde a uma flag de versao". #>
    param(
        [string]   $Rotulo,
        [string]   $Exe,
        [string[]] $Argumentos,
        [string]   $Dica,
        [switch]   $Opcional
    )

    if (-not (Test-Comando $Exe)) {
        if ($Opcional) { Write-Aviso "$Rotulo - '$Exe' nao encontrado (opcional)" $Dica }
        else           { Write-Falha "$Rotulo - '$Exe' nao encontrado no PATH" $Dica }
        return
    }

    $r = Get-SaidaComando -Exe $Exe -Argumentos $Argumentos
    $primeira = ($r.Texto -split "`n" | Where-Object { $_.Trim() } | Select-Object -First 1)

    if ($r.Ok -and $primeira) { Write-Ok $Rotulo $primeira.Trim() }
    elseif ($Opcional)        { Write-Aviso "$Rotulo - instalado, mas nao respondeu" $Dica }
    else                      { Write-Falha "$Rotulo - instalado, mas nao respondeu" $Dica }
}

Write-Host ''
Write-Host '=============================================' -ForegroundColor Cyan
Write-Host ' Verificador de ambiente - Semana 00 (CEIA)  ' -ForegroundColor Cyan
Write-Host '=============================================' -ForegroundColor Cyan
Write-Host "Maquina: $env:COMPUTERNAME | Usuario: $env:USERNAME | $(Get-Date -Format 'dd/MM/yyyy HH:mm')" -ForegroundColor DarkGray

# ------------------------------------------------------------------ Git -----
Write-Secao 'Git e GitHub'

Test-Ferramenta -Rotulo 'git' -Exe 'git' -Argumentos @('--version') `
    -Dica 'Instale em https://git-scm.com/download/win e reabra o terminal.'

if (Test-Comando 'git') {
    $nome  = (Get-SaidaComando -Exe 'git' -Argumentos @('config', '--global', 'user.name')).Texto
    $email = (Get-SaidaComando -Exe 'git' -Argumentos @('config', '--global', 'user.email')).Texto

    if ($nome)  { Write-Ok 'git config user.name' $nome }
    else        { Write-Falha 'git config user.name nao definido' 'git config --global user.name "Seu Nome"' }

    if ($email) { Write-Ok 'git config user.email' $email }
    else        { Write-Falha 'git config user.email nao definido' 'git config --global user.email "voce@exemplo.com"' }
}

$chaves = @()
$dirSsh = Join-Path $HOME '.ssh'
if (Test-Path $dirSsh) {
    $chaves = @(Get-ChildItem -Path $dirSsh -Filter '*.pub' -File -ErrorAction SilentlyContinue)
}
if ($chaves.Count -gt 0) {
    Write-Ok 'Chave SSH encontrada' (($chaves | ForEach-Object { $_.Name }) -join ', ')
}
else {
    Write-Falha 'Nenhuma chave SSH publica em ~/.ssh' 'ssh-keygen -t ed25519 -C "voce@exemplo.com"'
}

if ($PularRede) {
    Write-Aviso 'SSH para o GitHub - pulado (-PularRede)' ''
}
elseif (-not (Test-Comando 'ssh')) {
    Write-Falha 'ssh nao encontrado no PATH' 'Ative o OpenSSH Client em Configuracoes > Aplicativos > Recursos opcionais.'
}
else {
    $r = Get-SaidaComando -Exe 'ssh' -Argumentos @(
        '-T', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=accept-new',
        '-o', 'ConnectTimeout=10', 'git@github.com'
    )
    # O GitHub sempre encerra com exit code 1; o que vale e a mensagem.
    if ($r.Texto -match 'successfully authenticated') {
        $usuario = if ($r.Texto -match 'Hi ([^!]+)!') { $Matches[1] } else { '?' }
        Write-Ok 'SSH para o GitHub' "autenticado como $usuario"
    }
    elseif ($r.Texto -match 'Permission denied') {
        Write-Falha 'SSH para o GitHub - Permission denied' 'A chave publica ainda nao foi adicionada em https://github.com/settings/keys'
    }
    else {
        Write-Falha 'SSH para o GitHub falhou' ($r.Texto -split "`n" | Select-Object -First 1)
    }
}

# --------------------------------------------------------------- Python -----
Write-Secao 'Python'

# Pegamos o primeiro que REALMENTE responde: o Windows traz um 'python3.exe'
# (e as vezes 'python.exe') que e so um atalho para a Microsoft Store.
$pythonExe = $null
foreach ($candidato in @('python', 'python3')) {
    if (-not (Test-Comando $candidato)) { continue }
    $teste = Get-SaidaComando -Exe $candidato -Argumentos @('--version')
    if ($teste.Ok -and $teste.Texto -match 'Python \d') { $pythonExe = $candidato; break }
}

if ($pythonExe) {
    Test-Ferramenta -Rotulo 'python' -Exe $pythonExe -Argumentos @('--version') -Dica ''
    Test-Ferramenta -Rotulo 'pip' -Exe $pythonExe -Argumentos @('-m', 'pip', '--version') `
        -Dica 'Reinstale o Python marcando a opcao "pip" / rode: python -m ensurepip --upgrade'

    $venv = Get-SaidaComando -Exe $pythonExe -Argumentos @('-m', 'venv', '--help')
    if ($venv.Ok) { Write-Ok 'modulo venv' 'disponivel' }
    else          { Write-Falha 'modulo venv indisponivel' 'Reinstale o Python a partir de python.org (a versao da Store vem capada).' }
}
else {
    Write-Falha 'python nao encontrado no PATH' 'Instale em https://www.python.org/downloads/ marcando "Add python.exe to PATH".'
}

# --------------------------------------------------------------- Docker -----
Write-Secao 'Docker'

if (-not (Test-Comando 'docker')) {
    Write-Falha 'docker nao encontrado no PATH' 'Instale o Docker Desktop: https://docs.docker.com/desktop/install/windows-install/'
}
else {
    Test-Ferramenta -Rotulo 'docker (cliente)' -Exe 'docker' -Argumentos @('--version') -Dica ''

    $servidor = Get-SaidaComando -Exe 'docker' -Argumentos @('info', '--format', '{{.ServerVersion}}')
    if ($servidor.Ok -and $servidor.Texto) {
        Write-Ok 'docker daemon respondendo' "server $($servidor.Texto)"
    }
    else {
        Write-Falha 'docker daemon nao respondeu' 'Abra o Docker Desktop e espere o icone ficar verde ("Engine running").'
    }

    $compose = Get-SaidaComando -Exe 'docker' -Argumentos @('compose', 'version')
    if ($compose.Ok) { Write-Ok 'docker compose' ($compose.Texto -split "`n" | Select-Object -First 1) }
    else             { Write-Aviso 'docker compose nao disponivel' 'Atualize o Docker Desktop (Compose V2 ja vem embutido).' }
}

# ------------------------------------------------------------------ WSL -----
Write-Secao 'WSL2'

if (-not (Test-Comando 'wsl')) {
    Write-Falha 'wsl nao encontrado' 'Rode em um PowerShell como administrador: wsl --install'
}
else {
    # Pedimos ao proprio Linux que responda: a saida vem em UTF-8 limpo,
    # diferente de "wsl --status", que sai em UTF-16 e embaralha no console.
    $uname = Get-SaidaComando -Exe 'wsl' -Argumentos @('-e', 'uname', '-sr')
    if ($uname.Ok -and $uname.Texto -match 'Linux') {
        Write-Ok 'WSL2 com distro funcionando' $uname.Texto
    }
    else {
        Write-Falha 'WSL instalado, mas sem distro utilizavel' 'wsl --install -d Ubuntu  (e reinicie a maquina)'
    }
}

# ---------------------------------------------------------------- gcloud ----
Write-Secao 'Google Cloud (opcional nesta semana)'

if (-not (Test-Comando 'gcloud')) {
    Write-Aviso 'gcloud nao encontrado (opcional)' 'So e obrigatorio a partir da Semana 06: https://cloud.google.com/sdk/docs/install'
}
else {
    Test-Ferramenta -Rotulo 'gcloud' -Exe 'gcloud' -Argumentos @('--version') -Opcional -Dica ''

    $conta = Get-SaidaComando -Exe 'gcloud' -Argumentos @('config', 'get-value', 'account')
    if ($conta.Ok -and $conta.Texto -and $conta.Texto -notmatch '(?i)unset') {
        Write-Ok 'gcloud autenticado' ($conta.Texto -split "`n" | Select-Object -First 1)
    }
    else {
        Write-Aviso 'gcloud sem conta ativa' 'gcloud auth login'
    }

    $projeto = Get-SaidaComando -Exe 'gcloud' -Argumentos @('config', 'get-value', 'project')
    if ($projeto.Ok -and $projeto.Texto -and $projeto.Texto -notmatch '(?i)unset') {
        Write-Ok 'Projeto GCP configurado' ($projeto.Texto -split "`n" | Select-Object -First 1)
    }
    else {
        Write-Aviso 'Nenhum projeto GCP configurado' 'gcloud config set project <SEU_PROJETO>'
    }
}

# --------------------------------------------------- Maquina 4090 do lab ----
Write-Secao 'Maquina 4090 do laboratorio'

if ($PularRede) {
    Write-Aviso 'Acesso ao lab - pulado (-PularRede)' ''
}
elseif (-not $HostLab) {
    Write-Aviso 'Host do lab nao informado' 'Rode: .\verificar-ambiente.ps1 -HostLab usuario@servidor  (o host sai no Discord)'
}
elseif (-not (Test-Comando 'ssh')) {
    Write-Falha 'ssh nao encontrado no PATH' 'Ative o OpenSSH Client nos recursos opcionais do Windows.'
}
else {
    $r = Get-SaidaComando -Exe 'ssh' -Argumentos @(
        '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=accept-new',
        '-o', 'ConnectTimeout=10', $HostLab,
        'nvidia-smi --query-gpu=name --format=csv,noheader || hostname'
    )
    if ($r.Ok -and $r.Texto) { Write-Ok "SSH em $HostLab" ($r.Texto -split "`n" | Select-Object -First 1) }
    else                     { Write-Falha "SSH em $HostLab falhou" ($r.Texto -split "`n" | Select-Object -First 1) }
}

# ---------------------------------------------------------------- Resumo ----
Write-Host ''
Write-Host '---------------------------------------------' -ForegroundColor Cyan
if ($script:Falhas -eq 0) {
    Write-Host "$OK Ambiente pronto! ($script:Avisos aviso(s) nao bloqueante(s))" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "$FALHA $script:Falhas item(ns) faltando e $script:Avisos aviso(s)." -ForegroundColor Red
    Write-Host '   Resolva os itens em vermelho e rode de novo. Travou? Poste a saida no Discord.' -ForegroundColor DarkGray
    exit 1
}
