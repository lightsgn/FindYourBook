#!/bin/bash
cd "$(dirname "$0")"

# Sanal ortam kontrolü
if [ ! -d ".venv" ]; then
    echo "Setting up the virtual environment... Please wait."
    python3 -m venv .venv
fi

# Ortamı aktif et
source .venv/bin/activate

# Kütüphaneleri yükle
echo "Checking the libraries..."
pip install -r requirements.txt > /dev/null 2>&1

# Tarayıcıyı aç (3 saniye sonra)
(sleep 3 && open "http://127.0.0.1:5000") &

# Başlat
echo "FindABook Is Starting..."
python3 main.py