#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from pathlib import Path
import config

def save_result(content: str, format: str, url: str) -> str:
    """Сохраняет результат в файл"""
    results_dir = config.STORAGE_DIR / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Генерируем имя файла
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    video_id = url.split("/")[-1].split("?")[0][:15]
    base_name = f"youtube_{video_id}_{timestamp}"
    
    filepath = results_dir / f"{base_name}.{format}"
    
    if format == "txt":
        _save_txt(filepath, content)
    elif format == "md":
        _save_md(filepath, content)
    elif format == "pdf":
        _save_pdf(filepath, content)
    
    return str(filepath)

def _save_txt(filepath: Path, content: str):
    """Сохранение в TXT"""
    clean = content.replace("###", "").replace("##", "").replace("#", "")
    clean = clean.replace("**", "").replace("__", "")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(clean)

def _save_md(filepath: Path, content: str):
    """Сохранение в Markdown"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def _save_pdf(filepath: Path, content: str):
    """Сохранение в PDF"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(str(filepath), pagesize=A4)
        width, height = A4
        
        y = height - 50
        for line in content.split("\n"):
            if y < 50:
                c.showPage()
                y = height - 50
            c.drawString(50, y, line[:80])
            y -= 15
        
        c.save()
    except Exception as e:
        # Fallback к TXT
        filepath = filepath.with_suffix('.txt')
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   ⚠️  PDF не создан: {e}. Сохранено как .txt")
