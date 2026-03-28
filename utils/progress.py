#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from datetime import datetime

class ProgressDisplay:
    """Отображает прогресс обработки с красивыми индикаторами"""
    
    def __init__(self):
        self.current_step = 0
        self.total_steps = 0
        self.start_time = None
    
    def start(self, total_steps: int):
        """Начинает отображение прогресса"""
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = datetime.now()
        print("\n" + "=" * 70)
        print("  🔄 ОБРАБОТКА")
        print("=" * 70)
    
    def update(self, step_name: str, status: str = "in_progress"):
        """Обновляет статус шага"""
        self.current_step += 1
        
        icons = {
            "in_progress": "⏳",
            "done": "✅",
            "error": "❌",
            "warning": "⚠️"
        }
        
        icon = icons.get(status, "⏳")
        elapsed = datetime.now() - self.start_time if self.start_time else None
        elapsed_str = str(elapsed).split(".")[0] if elapsed else "00:00"
        
        print(f"  {icon} Шаг {self.current_step}/{self.total_steps}: {step_name}")
        if status == "done":
            print(f"     ⏱ Затрачено времени: {elapsed_str}")
        sys.stdout.flush()
    
    def finish(self):
        """Завершает отображение прогресса"""
        total_elapsed = datetime.now() - self.start_time if self.start_time else None
        total_str = str(total_elapsed).split(".")[0] if total_elapsed else "00:00"
        print("=" * 70)
        print(f"  ✅ ОБРАБОТКА ЗАВЕРШЕНА (всего: {total_str})")
        print("=" * 70 + "\n")
        sys.stdout.flush()

def print_status(message: str, icon: str = "ℹ️"):
    """Выводит статусное сообщение"""
    print(f"  {icon} {message}")
    sys.stdout.flush()

def animate_dots(duration: float = 1.0, message: str = "Загрузка"):
    """Анимация точек во время ожидания"""
    for i in range(int(duration * 2)):
        dots = "." * ((i % 3) + 1)
        print(f"\r  ⏳ {message}{dots}        ", end="", flush=True)
        time.sleep(0.5)
    print("\r" + " " * 50 + "\r", end="", flush=True)
