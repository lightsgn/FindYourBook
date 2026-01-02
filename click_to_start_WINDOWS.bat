@echo off
cd /d "%~dp0"

:: Sanal ortam kontrolü
if not exist .venv (
    echo Setting up the virtual environment... Please wait.
    python -m venv .venv
)

:: Ortamı aktif et
call .venv\Scripts\activate

:: Kütüphaneleri yükle
echo Checking the libraries...
pip install -r requirements.txt >nul 2>&1

:: Tarayıcıyı aç
start "" "http://127.0.0.1:5000"

:: Başlat
echo FindABook Is Starting...
python -m app.main
pause