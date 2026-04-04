@echo off
echo ==========================================
echo Iniciando o Assistente de Pedidos...
echo ==========================================
cd /d "%~dp0"
uv run main.py
pause