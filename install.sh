#!/bin/bash
# YouTube AI Agent — Автоустановщик (macOS/Linux)

set -e

echo "======================================================================"
echo "           🤖 YouTube AI Agent — Автоустановка"
echo "======================================================================"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Проверка Python
echo "🔍 Проверка Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python $PYTHON_VERSION найден${NC}"
else
    echo -e "${RED}❌ Python 3 не найден!${NC}"
    echo "Установите Python 3.10+ с https://www.python.org"
    exit 1
fi

# Проверка и установка Homebrew (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo "🔍 Проверка Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}⏳ Установка Homebrew...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        echo -e "${GREEN}✅ Homebrew найден${NC}"
    fi
fi

# Установка FFmpeg
echo ""
echo "🔍 Проверка FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}⏳ Установка FFmpeg...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install ffmpeg
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt update && sudo apt install -y ffmpeg
    fi
    echo -e "${GREEN}✅ FFmpeg установлен${NC}"
else
    echo -e "${GREEN}✅ FFmpeg найден${NC}"
fi

# Установка Ollama
echo ""
echo "🔍 Проверка Ollama..."
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}⏳ Установка Ollama...${NC}"
    curl -fsSL https://ollama.com/install.sh | sh
    echo -e "${GREEN}✅ Ollama установлен${NC}"
else
    echo -e "${GREEN}✅ Ollama найден${NC}"
fi

# Запуск Ollama сервера
echo ""
echo "🚀 Запуск Ollama сервера..."
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve &
    sleep 5
    echo -e "${GREEN}✅ Ollama сервер запущен${NC}"
else
    echo -e "${GREEN}✅ Ollama сервер уже работает${NC}"
fi

# Установка Python зависимостей
echo ""
echo "📦 Установка Python зависимостей..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
echo -e "${GREEN}✅ Зависимости установлены${NC}"

# Скачивание модели
echo ""
echo "🤖 Скачивание модели (может занять 5-10 минут)..."
ollama pull qwen3.5:9b
echo -e "${GREEN}✅ Модель загружена${NC}"

# Финал
echo ""
echo "======================================================================"
echo -e "${GREEN}                    ✅ УСТАНОВКА ЗАВЕРШЕНА${NC}"
echo "======================================================================"
echo ""
echo "🚀 Запуск:"
echo "   python3 main.py"
echo ""
echo "======================================================================"
