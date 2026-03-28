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
    def __init__(self):
        self.cache = CacheService(config.STORAGE_DIR / "cache")
        self.progress = ProgressDisplay()
    
    def process(self, url: str, task: str) -> str:
        """Полный пайплайн обработки видео"""
        video_id = extract_video_id(url)
        
        # Инициализация прогресса (4 шага)
        self.progress.start(4)
        
        # Шаг 1: Проверка кэша
        self.progress.update("Проверка кэша", "in_progress")
        transcript = self.cache.get_transcript(video_id)
        
        if not transcript:
            # Шаг 2: Скачивание и транскрибация
            self.progress.update("Скачивание аудио", "done")
            
            self.progress.update("Транскрибация через Whisper", "in_progress")
            transcriber = TranscriptionService()
            audio_path = download_audio(url)
            transcript = transcriber.transcribe(audio_path)
            transcript = clean_transcript(transcript)
            self.cache.save_transcript(video_id, transcript)
            self.progress.update("Транскрибация через Whisper", "done")
        else:
            self.progress.update("Скачивание аудио", "done")
            self.progress.update("Транскрибация через Whisper", "done")
            print_status("Использован кэшированный транскрипт", "♻️")
        
        # Шаг 3: Анализ через LLM
        self.progress.update("Анализ через нейросеть", "in_progress")
        prompt = self._build_prompt(task, transcript)
        llm = LLMEngine()
        response = llm.generate(prompt)
        self.progress.update("Анализ через нейросеть", "done")
        
        # Шаг 4: Форматирование
        self.progress.update("Форматирование результата", "in_progress")
        info = get_video_info(url)
        result = self._format_result(info, task, response)
        self.progress.update("Форматирование результата", "done")
        
        self.progress.finish()
        
        return result
    
    def _build_prompt(self, task: str, transcript: str) -> str:
        """Формирует промпт с задачей пользователя"""
        max_chars = 15000
        if len(transcript) > max_chars:
            transcript = transcript[:max_chars] + "... (текст обрезан из-за длины)"
        
        return f"""Ты — умный ассистент для анализа видео на YouTube.

ЗАДАЧА ОТ ПОЛЬЗОВАТЕЛЯ:
{task}

ТРАНСКРИПТ ВИДЕО:
{transcript}

ИНСТРУКЦИИ:
1. Внимательно изучи транскрипт
2. Выполни задачу пользователя максимально точно
3. Если информации нет в видео — честно напиши "В видео не найдено информации по этому вопросу"
4. Форматируй ответ красиво (списки, заголовки если нужно)
5. Отвечай на русском языке

ОТВЕТ:"""
    
    def _format_result(self, info: dict, task: str, response: str) -> str:
        """Форматирует итоговый результат"""
        duration = info.get('duration', 0)
        duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "Неизвестно"
        
        return f"""📹 Видео: {info.get('title', 'Неизвестно')}
⏱ Длительность: {duration_str}
👤 Канал: {info.get('channel', 'Неизвестно')}

📋 ЗАДАЧА:
{task}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 ОТВЕТ:
{response}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
