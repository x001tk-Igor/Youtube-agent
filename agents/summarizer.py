#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from services.cache import CacheService
from services.youtube_dl import download_audio, get_video_info, extract_video_id
from services.transcription import TranscriptionService
from services.llm_engine import LLMEngine
from utils.text_cleaning import clean_transcript
from utils.progress import ProgressDisplay, print_status
import config

class VideoSummarizer:
    """
    Класс для обработки и анализа видео с YouTube
    Поддерживает 3 уровня детализации: краткий, стандартный, подробный
    """
    
    def __init__(self, detail_level: str = "standard"):
        """
        Инициализация суммаризатора
        
        Args:
            detail_level: Уровень детализации ("brief", "standard", "detailed")
        """
        self.cache = CacheService(config.STORAGE_DIR / "cache")
        self.progress = ProgressDisplay()
        self.detail_level = detail_level
        
        # Настройки в зависимости от уровня детализации
        self.settings = self._get_detail_settings()
    
    def _get_detail_settings(self) -> dict:
        """Получает настройки для текущего уровня детализации"""
        settings = {
            "brief": {
                "max_chars": 10000,
                "max_tokens": 1024,
                "temperature": 0.3,
                "instruction": "Ответь кратко, только самое главное, без лишних деталей. 100-300 слов."
            },
            "standard": {
                "max_chars": 20000,
                "max_tokens": 2048,
                "temperature": 0.5,
                "instruction": "Ответь подробно, с деталями и примерами. 400-700 слов."
            },
            "detailed": {
                "max_chars": 30000,
                "max_tokens": 4096,
                "temperature": 0.6,
                "instruction": "Ответь МАКСИМАЛЬНО подробно, раскрой все аспекты, цитируй видео, пиши минимум 800-1500 слов."
            }
        }
        return settings.get(self.detail_level, settings["standard"])
    
    def process(self, url: str, task: str) -> str:
        """
        Полный пайплайн обработки видео
        
        Args:
            url: Ссылка на видео YouTube
            task: Задача от пользователя (что нужно найти/анализировать)
        
        Returns:
            str: Форматированный результат анализа
        """
        video_id = extract_video_id(url)
        
        # Инициализация прогресса (5 шагов)
        self.progress.start(5)
        
        # Шаг 1: Проверка кэша
        self.progress.update("Проверка кэша транскриптов", "in_progress")
        transcript = self.cache.get_transcript(video_id)
        
        if not transcript:
            self.progress.update("Проверка кэша транскриптов", "done")
            
            # Шаг 2: Скачивание аудио
            self.progress.update("Скачивание аудио с YouTube", "in_progress")
            audio_path = download_audio(url)
            self.progress.update("Скачивание аудио с YouTube", "done")
            
            # Шаг 3: Транскрибация
            self.progress.update("Транскрибация через Whisper", "in_progress")
            transcriber = TranscriptionService()
            transcript = transcriber.transcribe(audio_path)
            transcript = clean_transcript(transcript)
            self.cache.save_transcript(video_id, transcript)
            self.progress.update("Транскрибация через Whisper", "done")
        else:
            self.progress.update("Проверка кэша транскриптов", "done")
            self.progress.update("Скачивание аудио с YouTube", "done")
            self.progress.update("Транскрибация через Whisper", "done")
            print_status("Использован кэшированный транскрипт", "♻️")
        
        # Шаг 4: Анализ через LLM
        self.progress.update("Анализ через нейросеть", "in_progress")
        prompt = self._build_prompt(task, transcript)
        llm = LLMEngine()
        response = llm.generate(prompt, max_tokens=self.settings["max_tokens"])
        self.progress.update("Анализ через нейросеть", "done")
        
        # Шаг 5: Форматирование
        self.progress.update("Форматирование результата", "in_progress")
        info = get_video_info(url)
        result = self._format_result(info, task, response)
        self.progress.update("Форматирование результата", "done")
        
        self.progress.finish()
        
        return result
    
    def _build_prompt(self, task: str, transcript: str) -> str:
        """
        Формирует промпт с задачей пользователя
        
        Args:
            task: Задача от пользователя
            transcript: Текст транскрипции видео
        
        Returns:
            str: Готовый промпт для LLM
        """
        # Ограничиваем контекст согласно настройкам детализации
        max_chars = self.settings["max_chars"]
        if len(transcript) > max_chars:
            transcript = transcript[:max_chars] + "\n\n[... текст обрезан из-за длины ...]"
        
        # Определяем уровень детализации для пользователя
        detail_labels = {
            "brief": "КРАТКИЙ",
            "standard": "ПОДРОБНЫЙ",
            "detailed": "МАКСИМАЛЬНО ПОДРОБНЫЙ"
        }
        detail_label = detail_labels.get(self.detail_level, "ПОДРОБНЫЙ")
        
        return f"""Ты — экспертный аналитик видео контента на YouTube. 
Твоя специализация — глубокий анализ транскриптов и выявление ключевой информации.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 РЕЖИМ РАБОТЫ: {detail_label}

📋 ЗАДАЧА ОТ ПОЛЬЗОВАТЕЛЯ:
{task}

{self.settings["instruction"]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 ТРАНСКРИПТ ВИДЕО:
{transcript}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 ТРЕБОВАНИЯ К ФОРМАТУ ОТВЕТА:

1. **СТРУКТУРА** (обязательно используй эти разделы):

   🎬 ОБЗОР ВИДЕО
   - Основная тема (2-3 предложения)
   - Контекст и цель видео
   - Для кого этот контент

   🎯 КЛЮЧЕВЫЕ ТЕЗИСЫ
   - Перечисли все главные идеи (каждую с пояснением)
   - Минимум 3-5 тезисов для подробного режима
   - Каждый тезис с примером из видео

   📊 ФАКТЫ И ЦИФРЫ
   - Все упомянутые числа, даты, статистика
   - Цены, проценты, сроки, количества
   - Форматируй как список

   💡 ИДЕИ И РЕКОМЕНДАЦИИ
   - Что советует автор
   - Практические шаги если есть
   - Инструменты и сервисы которые упоминаются

   ⚠️ ПРЕДУПРЕЖДЕНИЯ И РИСКИ
   - На что обращает внимание автор
   - Возможные проблемы
   - Ограничения которые упоминаются

   🔗 УПОМИНАНИЯ
   - Сайты, сервисы, приложения
   - Книги, курсы, ресурсы
   - Люди и компании

   📌 ЦИТАТЫ
   - 2-3 ключевые цитаты дословно (в кавычках)
   - Самые важные фразы из видео

   ❓ ОТКРЫТЫЕ ВОПРОСЫ
   - Что осталось нераскрытым
   - Что требует дополнительного изучения

2. **ДЕТАЛИЗАЦИЯ**:
   - Цитируй конкретные фразы из транскрипта (в кавычках)
   - Указывай примерные таймкоды если возможно
   - Раскрывай контекст каждого утверждения
   - Объясняй специальные термины

3. **ЕСЛИ ИНФОРМАЦИИ НЕТ**:
   - Честно напиши "В видео эта тема не раскрывается"
   - Но укажи что БЫЛО сказано по смежным вопросам
   - Не выдумывай информацию которой нет

4. **ЯЗЫК И СТИЛЬ**:
   - Отвечай на русском языке
   - Профессионально но доступно
   - Избегай воды и общих фраз
   - Каждая фраза должна нести ценность

5. **ФОРМАТИРОВАНИЕ**:
   - Используй жирный текст для ключевых моментов
   - Используй списки для перечислений
   - Используй эмодзи для навигации по разделам
   - Разделяй разделы линиями ━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

НАЧНИ АНАЛИЗ СЕЙЧАС. ПИШИ МАКСИМАЛЬНО ПОДРОБНО И СТРУКТУРИРОВАНО:

"""
    
    def _format_result(self, info: dict, task: str, response: str) -> str:
        """
        Форматирует итоговый результат
        
        Args:
            info: Метаданные видео (название, длительность, канал)
            task: Исходная задача от пользователя
            response: Ответ от LLM
        
        Returns:
            str: Форматированный результат
        """
        duration = info.get('duration', 0)
        duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "Неизвестно"
        
        # Определяем уровень детализации для отображения
        detail_labels = {
            "brief": "Краткий",
            "standard": "Стандартный",
            "detailed": "Максимально подробный"
        }
        detail_label = detail_labels.get(self.detail_level, "Стандартный")
        
        return f"""╔══════════════════════════════════════════════════════════════════════╗
║                      📹 АНАЛИЗ ВИДЕО YOUTUBE                         ║
╠══════════════════════════════════════════════════════════════════════╣
║  Название: {info.get('title', 'Неизвестно')[:65]}{"..." if len(info.get('title', '')) > 65 else ""}
║  Длительность: {duration_str}
║  Канал: {info.get('channel', 'Неизвестно')[:50]}{"..." if len(info.get('channel', '')) > 50 else ""}
║  Режим анализа: {detail_label}
╚══════════════════════════════════════════════════════════════════════╝

📋 ЗАДАЧА ПОЛЬЗОВАТЕЛЯ:
   {task}

═══════════════════════════════════════════════════════════════════════

{response}

═══════════════════════════════════════════════════════════════════════

💾 Файл сохранён в: storage/results/
📅 Дата анализа: {__import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

═══════════════════════════════════════════════════════════════════════
"""
    
    def set_detail_level(self, level: str):
        """
        Меняет уровень детализации
        
        Args:
            level: "brief", "standard" или "detailed"
        """
        if level in ["brief", "standard", "detailed"]:
            self.detail_level = level
            self.settings = self._get_detail_settings()
            print_status(f"Уровень детализации: {level}", "✅")
        else:
            print_status(f"Неверный уровень детализации: {level}", "❌")
