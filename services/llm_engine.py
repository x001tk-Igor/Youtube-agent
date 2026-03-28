#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ollama
import config
from utils.progress import print_status
import sys

class LLMEngine:
    def __init__(self, model_name: str = None):
        """Инициализация LLM через Ollama"""
        self.model = model_name or config.LLM_MODEL
        self.host = config.OLLAMA_HOST
        
        # Ollama уже должен быть запущен через OllamaManager
        print_status(f"Подключение к LLM ({self.model})...", "🤖")
    
    def generate(self, prompt: str, max_tokens: int = 4096) -> str:
        """Генерирует ответ от LLM"""
        print_status("Отправка запроса к нейросети...", "💭")
        print(f"  📊 Размер промпта: {len(prompt)} символов")
        sys.stdout.flush()
        
        try:
            print_status("Генерация ответа (это может занять 1-3 минуты)...", "⏳")
            print_status("📈 Следите за загрузкой в мониторинге!", "💡")
            sys.stdout.flush()
            
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.5,
                    'num_predict': max_tokens
                },
                stream=True
            )
            
            full_response = ""
            token_count = 0
            for chunk in response:
                content = chunk['message']['content']
                full_response += content
                token_count += 1
                if token_count % 50 == 0:
                    print(f"\r  💭 Генерация: ~{token_count} токенов", end="", flush=True)
            
            print()
            print_status(f"Ответ получен ({token_count} токенов)", "✅")
            return full_response
            
        except Exception as e:
            print_status(f"Ошибка LLM: {str(e)}", "❌")
            print_status("Проверьте: 1) Ollama запущен 2) модель скачана", "💡")
            return f"❌ Ошибка LLM: {str(e)}"
    
    def check_model(self) -> bool:
        """Проверяет, доступна ли модель"""
        try:
            ollama.list()
            return True
        except:
            return False
