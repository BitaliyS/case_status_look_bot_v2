#!/bin/bash

# Скрипт для установки зависимостей в Google Cloud
echo "Начинаем установку зависимостей для бота..."

# Обновляем пакеты
sudo apt update

# Устанавливаем Python и необходимые пакеты
sudo apt install -y python3.11 python3.11-venv python3-pip git unzip wget

# Устанавливаем Chrome и Chromedriver
echo "Устанавливаем Chrome и Chromedriver..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Устанавливаем Chromedriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | awk -F'.' '{print $1}')
echo "Версия Chrome: $CHROME_VERSION"

# Скачиваем соответствующую версию Chromedriver
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION"
CHROMEDRIVER_VERSION=$(cat /tmp/chromedriver.zip)
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /tmp/
sudo mv /tmp/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Создаём виртуальное окружение
echo "Создаём виртуальное окружение..."
python3.11 -m venv .venv
source .venv/bin/activate

# Устанавливаем зависимости Python
echo "Устанавливаем Python зависимости..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Установка завершена!"
echo "Для запуска бота выполните:"
echo "source .venv/bin/activate"
echo "python3 bot/main.py" 