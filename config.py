#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube AI Agent — Конфигурация
Настройки проекта, модели, лимиты и параметры
"""

from pathlib import Path

# ============================================================
# БАЗОВЫЕ ПУТИ
# ============================================================

BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR / "storage"

# Создаём папки при импорте
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
(STORAGE_DIR / "results").mkdir(exist_ok=True)
(STORAGE_DIR / "cache").mkdir(exist_ok=True)
(STORAGE_DIR / "audio_cache").mkdir(exist_ok=True)
(STORAGE_DIR / "vectors").mkdir(exist_ok=True)

# ============================================================
# МОДЕЛИ
# ============================================================

LLM_MODEL = "qwen3.5:9b"              # Основная модель для анализа
WHISPER_MODEL = "medium"               # Модель транскрибации (tiny, base, small, medium, large)
EMBED_MODEL = "BAAI/bge-small-en-v1.5" # Модель для векторного поиска

# ============================================================
# ЛИМИТЫ ДЛЯ RTX 3060 12GB (и аналогичных)
# ============================================================

MAX_CONTEXT_TOKENS = 8192              # Максимум токенов в контексте
MAX_RESPONSE_TOKENS = 4096             # Максимум токенов в ответе LLM
AUDIO_CACHE_LIMIT_HOURS = 24           # Сколько хранить аудиофайлы
MAX_VIDEO_DURATION_SEC = 3600          # Максимальная длительность видео (1 час)
MAX_TRANSCRIPT_CHARS = 30000           # Максимум символов в транскрипте

# ============================================================
# ДЕТАЛИЗАЦИЯ ОТВЕТОВ
# ============================================================

DETAILED_MODE = True                   # Включить подробный режим по умолчанию
MIN_RESPONSE_WORDS = 500               # Минимум слов в ответе
USE_STRUCTURED_OUTPUT = True           # Использовать структуру с заголовками

# Уровни детализации
DETAIL_LEVELS = {
    "brief": {
        "max_chars": 10000,
        "max_tokens": 1024,
        "temperature": 0.3,
        "description": "Кратко — основные моменты (1-2 минуты чтения)"
    },
    "standard": {
        "max_chars": 20000,
        "max_tokens": 2048,
        "temperature": 0.5,
        "description": "Стандартно — подробно (3-5 минут чтения)"
    },
    "detailed": {
        "max_chars": 30000,
        "max_tokens": 4096,
        "temperature": 0.6,
        "description": "Максимально — максимально подробно (5-10 минут чтения)"
    }
}

# ============================================================
# OLLAMA НАСТРОЙКИ
# ============================================================

OLLAMA_HOST = "http://127.0.0.1:11434"
OLLAMA_TIMEOUT = 600                   # Таймаут запроса к LLM (секунды)
OLLAMA_AUTO_START = True               # Автоматически запускать Ollama сервер

# ============================================================
# YOUTUBE НАСТРОЙКИ
# ============================================================

REQUEST_TIMEOUT = 30                   # Таймаут запросов к YouTube
AUDIO_QUALITY = "192"                  # Качество аудио в kbps
AUDIO_FORMAT = "mp3"                   # Формат аудио

# ============================================================
# ЛОГИРОВАНИЕ
# ============================================================

LOG_LEVEL = "INFO"                     # DEBUG, INFO, WARNING, ERROR
LOG_FILE = STORAGE_DIR / "agent.log"   # Файл лога

# ============================================================
# ВЕКТОРНЫЙ ПОИСК (для каналов)
# ============================================================

VECTOR_STORE_PATH = STORAGE_DIR / "vectors"
CHUNK_SIZE = 1000                      # Размер чанка для векторизации
CHUNK_OVERLAP = 200                    # Перекрытие чанков
SIMILARITY_TOP_K = 5                   # Количество похожих результатов для поиска

# ============================================================
# ПРОВЕРКА КОНФИГУРАЦИИ
# ============================================================

def validate_config():
    """Проверяет корректность конфигурации"""
    import sys
    
    errors = []
    
    # Проверка путей
    if not STORAGE_DIR.exists():
        errors.append(f"Папка storage не создана: {STORAGE_DIR}")
    
    # Проверка модели
    if LLM_MODEL not in ["qwen3.5:9b", "qwen2.5:14b", "llama3.1:8b", "mistral:7b"]:
        errors.append(f"Неизвестная модель LLM: {LLM_MODEL}")
    
    # Проверка лимитов
    if MAX_RESPONSE_TOKENS > MAX_CONTEXT_TOKENS:
        errors.append("MAX_RESPONSE_TOKENS не может быть больше MAX_CONTEXT_TOKENS")
    
    if errors:
        print("⚠️  Ошибки в конфигурации:")
        for error in errors:
            print(f"  ❌ {error}")
        return False
    
    return True

# Автопроверка при импорте
if __name__ == "__main__":
    if validate_config():
        print("✅ Конфигурация в порядке")
    else:
        print("❌ Есть ошибки в конфигурации")
