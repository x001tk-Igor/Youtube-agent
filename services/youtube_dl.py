#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yt_dlp
import os
from pathlib import Path
import config
from utils.progress import print_status

class ProgressHook:
    """Хук для отображения прогресса скачивания"""
    def __init__(self):
        self.last_percent = 0
    
    def __call__(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', 'N/A').strip()
            if percent != self.last_percent:
                print(f"\r  ️  Загрузка аудио: {percent} ({speed})   ", end="", flush=True)
                self.last_percent = percent
        elif d['status'] == 'finished':
            print(f"\r  ✅ Загрузка аудио завершена                    ", end="", flush=True)
            print()

def download_audio(url: str) -> str:
    """Скачивает аудио с YouTube в формате MP3"""
    video_id = extract_video_id(url)
    output_path = config.STORAGE_DIR / "audio_cache" / f"{video_id}.mp3"
    
    # Если файл уже есть — не скачиваем повторно
    if output_path.exists():
        print_status("Аудио найдено в кэше", "✅")
        return str(output_path)
    
    print_status("Скачивание аудио с YouTube...", "⬇️")
    
    progress_hook = ProgressHook()
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': str(output_path).replace('.mp3', ''),
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [progress_hook],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print()
        return str(output_path)
    except Exception as e:
        print(f"\n  ❌ Ошибка скачивания: {str(e)}")
        raise

def extract_video_id(url: str) -> str:
    """Извлекает ID видео из URL"""
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    elif "v=" in url:
        return url.split("v=")[1].split("&")[0]
    return url.split("/")[-1]

def get_video_info(url: str) -> dict:
    """Получает метаданные видео"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            'title': info.get('title', 'Неизвестно'),
            'duration': info.get('duration', 0),
            'channel': info.get('uploader', 'Неизвестно'),
            'url': url,
            'video_id': extract_video_id(url)
        }

def is_channel_url(url: str) -> bool:
    """Проверяет, является ли ссылка каналом"""
    return "/channel/" in url or "/c/" in url or "/@" in url

def get_channel_videos_list(url: str) -> list:
    """Получает список всех видео канала"""
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
    }
    
    videos = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'entries' in info:
            for entry in info['entries']:
                if entry:
                    videos.append({
                        'id': entry.get('id', ''),
                        'title': entry.get('title', 'Без названия'),
                        'url': f"https://www.youtube.com/watch?v={entry.get('id', '')}"
                    })
    
    return videos
