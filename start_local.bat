@echo off
echo =====================================
echo     Iniciando YouTube Downloader     
echo =====================================
echo.

REM 
cd /d %~dp0

REM 
IF NOT EXIST "venv" (
    echo Ambiente virtual não encontrado. Criando novo ambiente...
    python -m venv venv
)

REM 
call venv\Scripts\activate

REM 
echo Instalando dependências...
pip install -r requirements.txt

REM 
echo Iniciando o aplicativo...
streamlit run app.py

pause
