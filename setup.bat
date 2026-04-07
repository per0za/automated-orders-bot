@echo off
title Assistente de Pedidos
echo ===================================================
echo Iniciando o Assistente de Pedidos com UV...
echo ===================================================

:: Garante que o script rode a partir da pasta exata onde este .bat esta salvo
cd /d "%~dp0"

:: 1. Verifica se o UV esta instalado neste computador
uv --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERRO] O gerenciador 'uv' nao foi encontrado neste computador!
    echo.
    echo Para instalar, abra o "PowerShell" no Windows e cole o comando abaixo:
    echo powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo.
    echo Apos a instalacao, feche esta janela preta e abra o arquivo .bat novamente.
    pause
    exit /b
)

:: 2. Sincroniza o projeto (instala bibliotecas novas se houver)
echo.
echo Sincronizando o projeto...
uv sync

echo.
echo ===================================================
echo Ambiente pronto! Rodando o robo...
echo ===================================================

:: 3. Roda o script principal (ja ajustado para main.py)
uv run main.py

:: Pausa no final para a janela nao fechar direto se der erro
pause