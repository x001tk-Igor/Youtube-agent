#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import shutil

def check_ffmpeg():
    """Проверяет наличие ffmpeg в системе"""
    if shutil.which("ffmpeg") is None:
        print("❌ FFmpeg не найден!")
        print()
        print("Установите командой:")
        print("  macOS:   brew install ffmpeg")
        print("  Ubuntu:  sudo apt install ffmpeg")
        print("  Windows: https://ffmpeg.org/download.html")
        print()
        return False
    print("✅ FFmpeg найден")
    return True

def check_ollama():
    """Проверяет наличие Ollama"""
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama найден")
            return True
    except:
        pass
    print("❌ Ollama не найден!")
    print("Установите с https://ollama.com")
    print()
    return False

def check_model(model_name: str):
    """Проверяет наличие модели в Ollama"""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if model_name in result.stdout:
            print(f"✅ Модель {model_name} найдена")
            return True
    except:
        pass
    print(f"❌ Модель {model_name} не найдена!")
    print(f"Скачайте командой: ollama pull {model_name}")
    print()
    return False

def install_requirements():
    """Устанавливает Python-зависимости"""
    print("📦 Установка Python-зависимостей...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print()

def main():
    print("=" * 60)
    print("   YouTube AI Agent — Проверка зависимостей")
    print("=" * 60)
    print()
    
    install_requirements()
    
    checks = [
        check_ffmpeg(),
        check_ollama(),
        check_model("qwen3.5:9b")
    ]
    
    print("=" * 60)
    if all(checks):
        print("✅ Все зависимости установлены!")
        print("Запустите: python3 main.py")
    else:
        print("⚠️  Некоторые зависимости отсутствуют!")
        print("Установите их и запустите этот скрипт снова.")
    print("=" * 60)

if __name__ == "__main__":
    main()
