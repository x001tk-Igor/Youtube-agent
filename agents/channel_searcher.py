#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Channel Searcher — Поиск информации по всему каналу YouTube
Использует кэшированные транскрипты для поиска по всем видео канала
"""

from services.youtube_dl import get_channel_videos_list
from services.cache import CacheService
from services.llm_engine import LLMEngine
from utils.progress import ProgressDisplay, print_status
import config

class ChannelSearcher:
    """
    Класс для поиска информации по всем видео канала
    Поддерживает 3 уровня детализации ответов
    """
    
    def __init__(self, detail_level: str = "standard"):
        """
        Инициализация поисковика по каналу
        
        Args:
            detail_level: Уровень детализации ("brief", "standard", "detailed")
        """
        self.cache = CacheService(config.STORAGE_DIR / "cache")
        self.llm = LLMEngine()
        self.progress = ProgressDisplay()
        self.detail_level = detail_level
        
        # Настройки в зависимости от уровня детализации
        self.settings = self._get_detail_settings()
    
    def _get_detail_settings(self) -> dict:
        """Получает настройки для текущего уровня детализации"""
        settings = {
            "brief": {
                "max_chars": 8000,
                "max_tokens": 1024,
                "min_matches": 1
            },
            "standard": {
                "max_chars": 10000,
                "max_tokens": 2048,
                "min_matches": 3
            },
            "detailed": {
                "max_chars": 12000,
                "max_tokens": 4096,
                "min_matches": 5
            }
        }
        return settings.get(self.detail_level, settings["standard"])
    
    def get_channel_videos(self, url: str) -> list:
        """
        Получает список всех видео канала
        
        Args:
            url: Ссылка на канал YouTube
        
        Returns:
            list: Список видео с метаданными
        """
        return get_channel_videos_list(url)
    
    def search_channel(self, videos: list, task: str) -> str:
        """
        Ищет информацию по всем видео канала
        
        Args:
            videos: Список видео канала
            task: Задача от пользователя (что искать)
        
        Returns:
            str: Форматированный результат поиска
        """
        found_results = []
        processed_count = 0
        skipped_count = 0
        total = len(videos)
        
        # Инициализация прогресса
        self.progress.start(total)
        
        for video in videos:
            processed_count += 1
            
            # Обновляем прогресс
            print(f"  📹 Видео {processed_count}/{total}: {video['title'][:50]}...")
            
            # Проверяем кэш
            transcript = self.cache.get_transcript(video['id'])
            if not transcript:
                skipped_count += 1
                print(f"     ℹ️  Пропущено (нет транскрипта)")
                continue
            
            # Ищем совпадения в транскрипте
            matches = self._search_in_transcript(transcript, task, video)
            if matches:
                found_results.append({
                    'video_id': video['id'],
                    'title': video['title'],
                    'url': video['url'],
                    'matches': matches
                })
                print(f"     ✅ Найдено совпадение!")
        
        self.progress.finish()
        
        return self._format_channel_results(found_results, task, total, processed_count, skipped_count)
    
    def _search_in_transcript(self, transcript: str, task: str, video: dict) -> str:
        """
        Ищет ответ на задачу в одном транскрипте
        
        Args:
            transcript: Текст транскрипции видео
            task: Задача от пользователя
            video: Метаданные видео
        
        Returns:
            str: Найденная информация или None
        """
        max_chars = self.settings["max_chars"]
        truncated = len(transcript) > max_chars
        transcript_chunk = transcript[:max_chars]
        
        prompt = f"""Ты аналитик видео контента. Пользователь ищет информацию по каналу YouTube.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 ЗАПРОС ПОЛЬЗОВАТЕЛЯ:
{task}

📹 ВИДЕО:
Название: {video['title']}
URL: {video['url']}

📄 ТЕКСТ ВИДЕО (транскрипт):
{transcript_chunk}
{"[... текст обрезан из-за длины ...]" if truncated else ""}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 ИНСТРУКЦИИ:

1. Найди ВСЕ упоминания по запросу в тексте
2. Для каждого упоминания выпиши:
   - Контекст (что обсуждалось вокруг)
   - Цитату (дословно если возможно, в кавычках)
   - Примерный таймкод (по сегментам транскрипта)
3. Если найдено несколько упоминаний — перечисли все
4. Если информации нет — верни только текст: "НЕ НАЙДЕНО"
5. Пиши подробно, не экономь на деталях

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 ОТВЕТ (пиши подробно, если найдено):

"""
        
        response = self.llm.generate(prompt, max_tokens=self.settings["max_tokens"])
        
        # Проверяем есть ли результат
        if "не найдено" in response.lower() and len(response.strip()) < 50:
            return None
        
        return response.strip()
    
    def _format_channel_results(self, results: list, task: str, total: int, processed: int, skipped: int) -> str:
        """
        Форматирует результаты поиска по каналу
        
        Args:
            results: Список найденных результатов
            task: Исходная задача от пользователя
            total: Всего видео на канале
            processed: Сколько обработано
            skipped: Сколько пропущено (нет транскрипта)
        
        Returns:
            str: Форматированный результат
        """
        timestamp = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not results:
            return f"""╔══════════════════════════════════════════════════════════════════════╗
║                    📺 ПОИСК ПО КАНАЛУ ЗАВЕРШЁН                       ║
╠══════════════════════════════════════════════════════════════════════╣
║  Статус: ❌ ИНФОРМАЦИЯ НЕ НАЙДЕНА
╚══════════════════════════════════════════════════════════════════════╝

📋 ЗАДАЧА ПОИСКА:
   {task}

═══════════════════════════════════════════════════════════════════════

📊 СТАТИСТИКА:
   • Всего видео на канале: {total}
   • Обработано видео: {processed}
   • Пропущено (нет транскрипта): {skipped}
   • Найдено совпадений: 0

═══════════════════════════════════════════════════════════════════════

💡 ВОЗМОЖНЫЕ ПРИЧИНЫ:

   1. Эта тема не обсуждалась в видео канала
   2. Информация есть в видео, но ещё не обработана (нет транскрипта)
   3. Запрос сформулирован слишком специфично

🔧 ЧТО МОЖНО СДЕЛАТЬ:

   • Обработайте больше видео канала (запустите снова)
   • Измените формулировку запроса
   • Попробуйте более общий запрос

═══════════════════════════════════════════════════════════════════════

📅 Дата поиска: {timestamp}

═══════════════════════════════════════════════════════════════════════
"""
        
        output = f"""╔══════════════════════════════════════════════════════════════════════╗
║                    📺 ПОИСК ПО КАНАЛУ ЗАВЕРШЁН                       ║
╠══════════════════════════════════════════════════════════════════════╣
║  Статус: ✅ НАЙДЕНО СОВПАДЕНИЙ: {len(results)}
╚══════════════════════════════════════════════════════════════════════╝

📋 ЗАДАЧА ПОИСКА:
   {task}

═══════════════════════════════════════════════════════════════════════

📊 СТАТИСТИКА:
   • Всего видео на канале: {total}
   • Обработано видео: {processed}
   • Пропущено (нет транскрипта): {skipped}
   • Найдено совпадений: {len(results)}

═══════════════════════════════════════════════════════════════════════

 НАЙДЕННЫЕ РЕЗУЛЬТАТЫ:

"""
        
        for i, res in enumerate(results, 1):
            output += f"""
┌──────────────────────────────────────────────────────────────────────┐
│  ВИДЕО #{i}: {res['title'][:55]}{"..." if len(res['title']) > 55 else ""}
├──────────────────────────────────────────────────────────────────────┤
│  URL: {res['url']}
├──────────────────────────────────────────────────────────────────────┤
│ 📄 НАЙДЕННАЯ ИНФОРМАЦИЯ:
│
{self._indent_text(res['matches'], 2)}
└──────────────────────────────────────────────────────────────────────┘
"""
        
        output += f"""
═══════════════════════════════════════════════════════════════════════

💡 РЕКОМЕНДАЦИИ:

   • Просмотрите найденные видео для полного контекста
   • Сохраните результат в файл для дальнейшего анализа
   • При необходимости уточните запрос и выполните поиск снова

═══════════════════════════════════════════════════════════════════════

📅 Дата поиска: {timestamp}

═══════════════════════════════════════════════════════════════════════
"""
        
        return output
    
    def _indent_text(self, text: str, spaces: int) -> str:
        """
        Добавляет отступы для форматирования
        
        Args:
            text: Текст для форматирования
            spaces: Количество отступов
        
        Returns:
            str: Текст с отступами
        """
        indent = "│ " + "  " * spaces
        return "\n".join([indent + line for line in text.split("\n")])
    
    def set_detail_level(self, level: str):
        """
        Меняет уровень детализации
        
        Args:
            level: "brief", "standard" или "detailed"
        """
        if level in ["brief", "standard", "detailed"]:
            self.detail_level = level
            self.settings = self._get_detail_settings()
            print_status(f"Уровень детализации поиска: {level}", "✅")
        else:
            print_status(f"Неверный уровень детализации: {level}", "❌")
