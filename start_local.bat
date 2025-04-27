@echo off
echo =====================================
echo     Iniciando YouTube Downloader     
echo =====================================
echo.

REM Ir para o diretório do script
cd /d %~dp0

REM Verificar se o ambiente virtual já existe
IF NOT EXIST "venv" (
    echo Ambiente virtual não encontrado. Criando novo ambiente...
    python -m venv venv
)

REM Ativar o ambiente virtual
call venv\Scripts\activate

REM Instalar dependências
echo Instalando dependências...
pip install -r requirements.txt

REM Rodar o Streamlit App
echo Iniciando o aplicativo...
streamlit run app.py

pause
