#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from services.youtube_dl import get_channel_videos_list
from services.cache import CacheService
from services.llm_engine import LLMEngine
import config

class ChannelSearcher:
    def __init__(self):
        self.cache = CacheService(config.STORAGE_DIR / "cache")
        self.llm = LLMEngine()
    
    def get_channel_videos(self, url: str) -> list:
        """Получает список всех видео канала"""
        return get_channel_videos_list(url)
    
    def search_channel(self, videos: list, task: str) -> str:
        """Ищет информацию по всем видео канала"""
        found_results = []
        processed_count = 0
        total = len(videos)
        
        for video in videos:
            processed_count += 1
            print(f"   → Видео {processed_count}/{total}: {video['title'][:50]}...")
            
            transcript = self.cache.get_transcript(video['id'])
            if not transcript:
                print(f"      ℹ️  Пропущено (нет транскрипта)")
                continue
            
            matches = self._search_in_transcript(transcript, task)
            if matches:
                found_results.append({
                    'video_id': video['id'],
                    'title': video['title'],
                    'url': video['url'],
                    'matches': matches
                })
        
        return self._format_channel_results(found_results, task, total)
    
    def _search_in_transcript(self, transcript: str, task: str) -> str:
        """Ищет ответ на задачу в одном транскрипте"""
        prompt = f"""Пользователь ищет информацию: {task}

Есть ли в этом тексте ответ или упоминание по запросу?
Если есть — выпиши цитату и контекст.
Если нет — верни только текст: НЕ НАЙДЕНО

Текст: {transcript[:8000]}

ОТВЕТ:"""
        
        response = self.llm.generate(prompt)
        
        if "не найдено" in response.lower() or len(response.strip()) < 20:
            return None
        return response.strip()
    
    def _format_channel_results(self, results: list, task: str, total: int) -> str:
        """Форматирует результаты поиска по каналу"""
        if not results:
            return f"""📺 Поиск по каналу завершён

📋 ЗАДАЧА:
{task}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ ИНФОРМАЦИЯ НЕ НАЙДЕНА

Просмотрено видео: {total}
К сожалению, в доступных транскриптах не найдено информации по вашему запросу.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        output = f"""📺 Поиск по каналу завершён

📋 ЗАДАЧА:
{task}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ НАЙДЕНО В {len(results)} ВИДЕО ИЗ {total}:

"""
        for i, res in enumerate(results, 1):
            output += f"""
┌─────────────────────────────────────────────────────────────────────────┐
│ 📹 Видео #{i}: {res['title'][:60]}
│ 🔗 URL: {res['url']}
├─────────────────────────────────────────────────────────────────────────┤
│  НАЙДЕННАЯ ИНФОРМАЦИЯ:
│
{self._indent_text(res['matches'], 2)}
└─────────────────────────────────────────────────────────────────────────┘
"""
        
        output += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        return output
    
    def _indent_text(self, text: str, spaces: int) -> str:
        """Добавляет отступы для форматирования"""
        indent = "│ " + "  " * spaces
        return "\n".join([indent + line for line in text.split("\n")])
