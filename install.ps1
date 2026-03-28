# YouTube AI Agent — Автоустановщик (Windows PowerShell)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "           YouTube AI Agent — Автоустановка" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Проверка Python
Write-Host "🔍 Проверка Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion найден" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 3 не найден!" -ForegroundColor Red
    Write-Host "Установите Python 3.10+ с https://www.python.org" -ForegroundColor Yellow
    Write-Host "⚠️  При установке отметьте 'Add Python to PATH'" -ForegroundColor Yellow
    exit 1
}

# Проверка FFmpeg
Write-Host ""
Write-Host "🔍 Проверка FFmpeg..." -ForegroundColor Yellow
if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    Write-Host "✅ FFmpeg найден" -ForegroundColor Green
} else {
    Write-Host "⚠️  FFmpeg не найден" -ForegroundColor Yellow
    Write-Host "Установите через winget:" -ForegroundColor Yellow
    Write-Host "  winget install Gyan.FFmpeg" -ForegroundColor Cyan
    Write-Host "Или скачайте с https://ffmpeg.org/download.html" -ForegroundColor Yellow
}

# Проверка Ollama
Write-Host ""
Write-Host "🔍 Проверка Ollama..." -ForegroundColor Yellow
if (Get-Command ollama -ErrorAction SilentlyContinue) {
    Write-Host "✅ Ollama найден" -ForegroundColor Green
} else {
    Write-Host "⏳ Установка Ollama..." -ForegroundColor Yellow
    Write-Host "⚠️  Скачайте с https://ollama.com/download/windows" -ForegroundColor Yellow
    Write-Host "⚠️  После установки запустите скрипт снова" -ForegroundColor Yellow
    exit 1
}

# Запуск Ollama сервера
Write-Host ""
Write-Host "🚀 Проверка Ollama сервера..." -ForegroundColor Yellow
$ollamaProcess = Get-Process ollama -ErrorAction SilentlyContinue
if (-not $ollamaProcess) {
    Write-Host "⏳ Запуск Ollama сервера..." -ForegroundColor Yellow
    Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 5
    Write-Host "✅ Ollama сервер запущен" -ForegroundColor Green
} else {
    Write-Host "✅ Ollama сервер уже работает" -ForegroundColor Green
}

# Установка Python зависимостей
Write-Host ""
Write-Host "📦 Установка Python зависимостей..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Write-Host "✅ Зависимости установлены" -ForegroundColor Green

# Скачивание модели
Write-Host ""
Write-Host "🤖 Скачивание модели (может занять 5-10 минут)..." -ForegroundColor Yellow
ollama pull qwen3.5:9b
Write-Host "✅ Модель загружена" -ForegroundColor Green

# Финал
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "                    ✅ УСТАНОВКА ЗАВЕРШЕНА" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Запуск:" -ForegroundColor Cyan
Write-Host "   python main.py" -ForegroundColor White
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
