#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import atexit
from services.youtube_dl import is_channel_url
from services.ollama_manager import OllamaManager
from agents.summarizer import VideoSummarizer
from agents.channel_searcher import ChannelSearcher
from utils.file_saver import save_result
from utils.progress import print_status
import config

# Глобальный менеджер Ollama
ollama_manager = None

def cleanup():
    """Очистка при выходе"""
    global ollama_manager
    # Не останавливаем Ollama сервер — он может использоваться другими приложениями
    pass

def print_header():
    """Выводит заголовок программы"""
    print("\n" + "=" * 70)
    print("           🤖 YouTube AI Agent — Локальный Ассистент")
    print("=" * 70)
    print("  Обработка видео и каналов через локальную LLM")
    print("  Нажми Ctrl+C для выхода")
    print("=" * 70 + "\n")

def print_system_info():
    """Выводит информацию о системе"""
    import platform
    import shutil
    
    print("=" * 70)
    print("  📊 ИНФОРМАЦИЯ О СИСТЕМЕ")
    print("=" * 70)
    print(f"  ОС: {platform.system()} {platform.release()}")
    print(f"  Python: {platform.python_version()}")
    print(f"  FFmpeg: {'✅' if shutil.which('ffmpeg') else '❌'}")
    
    # Проверка Ollama
    try:
        import ollama
        models = ollama.list()
        
        # Подсчёт количества моделей
        model_count = 0
        if hasattr(models, 'models'):
            model_count = len(models.models)
        elif isinstance(models, dict) and 'models' in models:
            model_count = len(models['models'])
        elif isinstance(models, list):
            model_count = len(models)
        
        print(f"  Ollama: ✅ ({model_count} моделей)")
    except:
        print(f"  Ollama: ❌ Не подключён")
    
    print(f"  Модель: {config.LLM_MODEL}")
    print("=" * 70 + "\n")

def get_url() -> str:
    """Запрашивает ссылку у пользователя"""
    while True:
        url = input("📎 Дайте ссылку на видео или канал YouTube:\n   > ").strip()
        if not url:
            print("   ❌ Ссылка не может быть пустой.\n")
            continue
        if "youtube.com" not in url and "youtu.be" not in url:
            print("   ❌ Это не ссылка на YouTube.\n")
            continue
        return url

def get_task() -> str:
    """Запрашивает задачу у пользователя"""
    print("\n📝 Какая задача? (опиши своими словами)")
    print("   Примеры:")
    print("   • просмотри видео и обобщи о чем там идет речь")
    print("   • выдели основные главные моменты")
    print("   • распиши все формулы, которые они там представили")
    print("   • найди все упоминания о ценах")
    print("   • найди информацию про X на всём канале")
    
    task = input("   > ").strip()
    
    if not task:
        task = "Сделай краткое содержание видео, выдели главные моменты"
        print(f"   ℹ️  Используется задача по умолчанию: {task}\n")
    else:
        print()
    
    return task

def get_save_format() -> str:
    """Запрашивает формат сохранения"""
    print("\n💾 В каком формате сохранить результат?")
    print("   1) txt — простой текст")
    print("   2) md — Markdown (с форматированием)")
    print("   3) pdf — PDF документ")
    print("   4) не сохранять")
    
    while True:
        choice = input("   > ").strip()
        if choice in ["1", "txt"]:
            return "txt"
        elif choice in ["2", "md"]:
            return "md"
        elif choice in ["3", "pdf"]:
            return "pdf"
        elif choice in ["4", "n", "no"]:
            return None
        else:
            print("   ❌ Выберите 1, 2, 3 или 4")

def process_video(url: str, task: str) -> str:
    """Обрабатывает одно видео"""
    summarizer = VideoSummarizer()
    result = summarizer.process(url, task)
    return result

def process_channel(url: str, task: str) -> str:
    """Обрабатывает весь канал"""
    print("\n📺 Обработка канала...")
    print("   ⚠️  Это может занять время (зависит от количества видео)")
    print()
    
    searcher = ChannelSearcher()
    videos = searcher.get_channel_videos(url)
    print(f"   Найдено видео: {len(videos)}")
    print()
    
    result = searcher.search_channel(videos, task)
    print("   ✅ Готово!\n")
    return result

def main():
    """Главная функция программы"""
    global ollama_manager
    
    print_header()
    print_system_info()
    
    try:
        # === ПРОВЕРКА И ЗАПУСК OLLAMA ===
        print_status("Проверка Ollama сервера...", "🔍")
        ollama_manager = OllamaManager()
        
        if not ollama_manager.ensure_running():
            print("\n❌ Не удалось запустить Ollama. Выход.")
            sys.exit(1)
        
        # Проверка модели (не блокирует, только предупреждает)
        ollama_manager.check_model(config.LLM_MODEL)
        
        print_status("Система готова к работе", "✅")
        print()
        
        # Регистрируем очистку при выходе
        atexit.register(cleanup)
        
        # === ОСНОВНОЙ ЦИКЛ ===
        url = get_url()
        task = get_task()
        is_channel = is_channel_url(url)
        
        if is_channel:
            print_status("Обнаружена ссылка на КАНАЛ", "📺")
            result = process_channel(url, task)
        else:
            print_status("Обнаружена ссылка на ВИДЕО", "🎬")
            result = process_video(url, task)
        
        # === ВЫВОД РЕЗУЛЬТАТА ===
        print("\n" + "=" * 70)
        print("                         📄 РЕЗУЛЬТАТ")
        print("=" * 70 + "\n")
        print(result)
        print("\n" + "=" * 70)
        
        # === СОХРАНЕНИЕ ===
        save_format = get_save_format()
        if save_format:
            filename = save_result(result, save_format, url)
            print(f"\n   ✅ Сохранено в: {filename}")
        
        # === ПОВТОРНЫЙ ЗАПУСК ===
        print("\n" + "=" * 70)
        again = input("🔄 Обработать ещё что-нибудь? (y/n): ").strip().lower()
        if again in ["y", "yes", "да", ""]:
            print("\n")
            main()  # Рекурсивный вызов
        else:
            print("\n👋 До встречи!\n")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n👋 Прервано пользователем.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {str(e)}\n")
        print_status("Попробуйте запустить снова", "💡")
        
        # Для отладки показываем полный traceback
        import traceback
        print("🔍 Детали ошибки:")
        traceback.print_exc()
        
        sys.exit(1)

if __name__ == "__main__":
    main()
