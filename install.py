#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube AI Agent — Кроссплатформенный установщик
Запускается через: python3 install.py
"""

import subprocess
import sys
import os
import platform
import shutil
from pathlib import Path

class Installer:
    def __init__(self):
        self.system = platform.system()
        self.python_cmd = "python3" if self.system != "Windows" else "python"
        self.pip_cmd = f"{self.python_cmd} -m pip"
    
    def print_header(self, text: str):
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70)
    
    def print_success(self, text: str):
        print(f"  ✅ {text}")
    
    def print_error(self, text: str):
        print(f"  ❌ {text}")
    
    def print_warning(self, text: str):
        print(f"  ⚠️  {text}")
    
    def print_info(self, text: str):
        print(f"  ℹ️  {text}")
    
    def run_command(self, cmd: list, shell: bool = False) -> bool:
        """Выполняет команду и возвращает успех"""
        try:
            subprocess.run(cmd, shell=shell, check=True)
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Ошибка: {e}")
            return False
        except Exception as e:
            self.print_error(f"Ошибка: {e}")
            return False
    
    def check_python(self) -> bool:
        """Проверяет Python"""
        self.print_header("🔍 Проверка Python")
        try:
            result = subprocess.run(
                [self.python_cmd, "--version"],
                capture_output=True, text=True, check=True
            )
            self.print_success(f"Python {result.stdout.strip()} найден")
            return True
        except:
            self.print_error("Python 3 не найден!")
            self.print_info("Установите с https://www.python.org")
            return False
    
    def check_ffmpeg(self) -> bool:
        """Проверяет FFmpeg"""
        self.print_header("🔍 Проверка FFmpeg")
        if shutil.which("ffmpeg"):
            self.print_success("FFmpeg найден")
            return True
        else:
            self.print_warning("FFmpeg не найден")
            if self.system == "Darwin":
                self.print_info("Установите: brew install ffmpeg")
            elif self.system == "Linux":
                self.print_info("Установите: sudo apt install ffmpeg")
            elif self.system == "Windows":
                self.print_info("Скачайте с https://ffmpeg.org/download.html")
            return False
    
    def check_ollama(self) -> bool:
        """Проверяет Ollama"""
        self.print_header("🔍 Проверка Ollama")
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True, text=True, check=True
            )
            self.print_success(f"Ollama {result.stdout.strip()} найден")
            return True
        except:
            self.print_warning("Ollama не найден")
            self.print_info("Установите с https://ollama.com")
            return False
    
    def install_requirements(self) -> bool:
        """Устанавливает Python зависимости"""
        self.print_header("📦 Установка Python зависимостей")
        return self.run_command([self.pip_cmd, "install", "-r", "requirements.txt"], shell=True)
    
    def pull_model(self, model_name: str = "qwen3.5:9b") -> bool:
        """Скачивает модель Ollama"""
        self.print_header(f"🤖 Скачивание модели {model_name}")
        self.print_info("Это может занять 5-10 минут в зависимости от интернета")
        return self.run_command(["ollama", "pull", model_name])
    
    def check_files(self) -> bool:
        """Проверяет наличие необходимых файлов"""
        self.print_header("📁 Проверка файлов проекта")
        required = ["main.py", "config.py", "requirements.txt"]
        missing = [f for f in required if not Path(f).exists()]
        
        if missing:
            self.print_error(f"Отсутствуют файлы: {', '.join(missing)}")
            return False
        
        self.print_success("Все файлы на месте")
        return True
    
    def install(self):
        """Запускает полную установку"""
        self.print_header("🤖 YouTube AI Agent — Установка")
        
        checks = [
            self.check_python(),
            self.check_files(),
        ]
        
        # Необязательные проверки
        self.check_ffmpeg()
        self.check_ollama()
        
        # Обязательная установка
        if not self.install_requirements():
            self.print_error("Не удалось установить зависимости")
            return False
        
        # Скачивание модели
        if shutil.which("ollama"):
            self.pull_model()
        
        # Финал
        self.print_header("✅ УСТАНОВКА ЗАВЕРШЕНА")
        print()
        print("🚀 Запуск: python3 main.py")
        print()
        
        return True

if __name__ == "__main__":
    installer = Installer()
    success = installer.install()
    sys.exit(0 if success else 1)
