@echo off
echo =====================================
echo      YouTube Downloader Launcher     
echo =====================================
echo.

REM Verifica se o ambiente virtual existe
IF NOT EXIST "venv" (
    echo Ambiente virtual não encontrado. Criando...
    python -m venv venv
)

REM Ativar ambiente virtual
call venv\Scripts\activate

REM Instala as dependências
echo Instalando dependências do projeto...
pip install -r requirements.txt

REM Rodar o Streamlit
echo Iniciando o aplicativo Streamlit...
streamlit run app.py

pause
