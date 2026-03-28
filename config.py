#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

# Базовая директория проекта
BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR / "storage"

# Создаём папки при импорте
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
(STORAGE_DIR / "results").mkdir(exist_ok=True)
(STORAGE_DIR / "cache").mkdir(exist_ok=True)
(STORAGE_DIR / "audio_cache").mkdir(exist_ok=True)
(STORAGE_DIR / "vectors").mkdir(exist_ok=True)

# === МОДЕЛИ ===
LLM_MODEL = "qwen3.5:9b"           # Основная модель
WHISPER_MODEL = "medium"            # Whisper: tiny, base, small, medium, large
EMBED_MODEL = "BAAI/bge-small-en-v1.5"  # Для векторного поиска

# === ЛИМИТЫ для RTX 3060 12GB ===
MAX_CONTEXT_TOKENS = 4096           # Максимум токенов в контексте
AUDIO_CACHE_LIMIT_HOURS = 24        # Сколько хранить аудиофайлы
MAX_VIDEO_DURATION_SEC = 3600       # Максимальная длительность видео (1 час)

# === OLLAMA ===
OLLAMA_HOST = "http://127.0.0.1:11434"
OLLAMA_TIMEOUT = 300                # Таймаут запроса к LLM (секунды)

# === YOUTUBE ===
REQUEST_TIMEOUT = 30                # Таймаут запросов к YouTube
