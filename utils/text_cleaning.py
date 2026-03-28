#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def clean_transcript(text: str) -> str:
    """Очищает транскрипт от мусора"""
    # Удаление таймкодов [00:00], [01:23]
    text = re.sub(r'\[\d{1,2}:\d{2}\]', '', text)
    
    # Удаление служебных пометок [Музыка], [Аплодисменты], (смех)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    
    # Удаление лишних пробелов
    text = re.sub(r'\s+', ' ', text)
    
    # Удаление повторяющихся слов (и и и → и)
    text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
    
    return text.strip()
