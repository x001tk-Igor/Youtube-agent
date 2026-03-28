#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from faster_whisper import WhisperModel
import torch
import config
from utils.progress import print_status

class TranscriptionService:
    def __init__(self):
        """Инициализация Whisper модели"""
        print_status("Загрузка модели транскрибации...", "🤖")
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        
        self.model = WhisperModel(
            config.WHISPER_MODEL,
            device=device,
            compute_type=compute_type
        )
        print_status("Модель транскрибации готова", "✅")
    
    def transcribe(self, audio_path: str) -> str:
        """Транскрибирует аудиофайл в текст"""
        print_status("Начинаю транскрибацию аудио...", "🎤")
        
        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5,
            language="ru"
        )
        
        # Прогресс транскрибации
        text_parts = []
        total_segments = None
        
        for segment in segments:
            text_parts.append(segment.text)
            # Показываем прогресс каждые 10 сегментов
            if len(text_parts) % 10 == 0:
                print(f"\r  🎤 Транскрибация: {len(text_parts)} сегментов обработано", end="", flush=True)
        
        print()
        text = " ".join(text_parts)
        print_status(f"Транскрибация завершена ({len(text)} символов)", "✅")
        return text
    
    def unload(self):
        """Освобождает память GPU"""
        del self.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
