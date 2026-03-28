#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from datetime import datetime, timedelta
import config

class CacheService:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_dir / "index.json"
        self.index = self._load_index()
    
    def _load_index(self) -> dict:
        """Загружает индекс кэша"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_index(self):
        """Сохраняет индекс кэша"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def get_transcript(self, video_id: str) -> str | None:
        """Получает транскрипт из кэша"""
        if video_id in self.index:
            file_path = self.cache_dir / f"{video_id}.txt"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        return None
    
    def save_transcript(self, video_id: str, text: str):
        """Сохраняет транскрипт в кэш"""
        file_path = self.cache_dir / f"{video_id}.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        self.index[video_id] = {
            'file': str(file_path),
            'created_at': datetime.now().isoformat()
        }
        self._save_index()
    
    def is_processed(self, video_id: str) -> bool:
        """Проверяет, обработано ли видео"""
        return video_id in self.index
    
    def cleanup_old_audio(self, hours: int = 24):
        """Удаляет старые аудиофайлы"""
        audio_dir = config.STORAGE_DIR / "audio_cache"
        cutoff = datetime.now() - timedelta(hours=hours)
        
        for file in audio_dir.glob("*.mp3"):
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            if mtime < cutoff:
                file.unlink()
