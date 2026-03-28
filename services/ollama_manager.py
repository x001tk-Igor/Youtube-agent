#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import socket
import sys
from utils.progress import print_status

class OllamaManager:
    """Управляет запуском и проверкой Ollama сервера"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 11434):
        self.host = host
        self.port = port
        self.process = None
    
    def is_running(self) -> bool:
        """Проверяет, запущен ли Ollama сервер"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            return result == 0
        except:
            return False
    
    def check_ollama_installed(self) -> bool:
        """Проверяет, установлен ли Ollama в системе"""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print_status(f"Ollama найден: {result.stdout.strip()}", "✅")
                return True
            return False
        except Exception as e:
            return False
    
    def start_server(self) -> bool:
        """Запускает Ollama сервер"""
        print_status("Запуск Ollama сервера...", "🚀")
        
        try:
            self.process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            print_status("Ожидание запуска сервера...", "⏳")
            for i in range(30):
                time.sleep(1)
                if self.is_running():
                    print_status("Ollama сервер запущен и готов", "✅")
                    return True
                if i % 5 == 0:
                    print(f"  ⏳ Ждём... ({i+1}/30 сек)", end="\r")
                    sys.stdout.flush()
            print()
            
            print_status("Сервер запущен (превышено время ожидания, но может работать)", "⚠️")
            return True
            
        except Exception as e:
            print_status(f"Ошибка запуска Ollama: {str(e)}", "❌")
            return False
    
    def ensure_running(self) -> bool:
        """Гарантирует, что Ollama запущен"""
        if not self.check_ollama_installed():
            print_status("Ollama не найден в системе!", "❌")
            print_status("Установите с https://ollama.com", "💡")
            return False
        
        if self.is_running():
            print_status("Ollama сервер уже запущен", "✅")
            return True
        
        return self.start_server()
    
    def stop_server(self):
        """Останавливает Ollama сервер"""
        if self.process:
            print_status("Остановка Ollama сервера...", "🛑")
            self.process.terminate()
            self.process.wait()
            print_status("Ollama сервер остановлен", "✅")
    
    def check_model(self, model_name: str) -> bool:
        """
        Проверяет наличие модели в Ollama
        Работает с разными версиями библиотеки ollama
        """
        try:
            import ollama
            
            # Получаем список моделей
            models_response = ollama.list()
            
            # Извлекаем список моделей из ответа (разные форматы)
            model_list = []
            
            # Формат 1: Pydantic объект с атрибутом models
            if hasattr(models_response, 'models'):
                model_list = models_response.models
            
            # Формат 2: dict с ключом models
            elif isinstance(models_response, dict) and 'models' in models_response:
                model_list = models_response['models']
            
            # Формат 3: прямой список
            elif isinstance(models_response, list):
                model_list = models_response
            
            # Извлекаем имена моделей
            model_names = []
            for model in model_list:
                # Pydantic объект с атрибутом model
                if hasattr(model, 'model'):
                    model_names.append(model.model)
                # Pydantic объект с атрибутом name
                elif hasattr(model, 'name'):
                    model_names.append(model.name)
                # dict с ключом model
                elif isinstance(model, dict) and 'model' in model:
                    model_names.append(model['model'])
                # dict с ключом name
                elif isinstance(model, dict) and 'name' in model:
                    model_names.append(model['name'])
                # Просто строка
                elif isinstance(model, str):
                    model_names.append(model)
            
            # Показываем доступные модели
            if model_names:
                print(f"  📋 Доступные модели: {', '.join(model_names)}")
            else:
                print(f"  ⚠️  Не удалось получить список моделей")
            
            # Проверяем наличие нужной модели
            model_base = model_name.split(':')[0]  # имя без тега (qwen3.5)
            model_tag = model_name.split(':')[1] if ':' in model_name else None  # тег (9b)
            
            model_found = False
            for name in model_names:
                name_base = name.split(':')[0]
                name_tag = name.split(':')[1] if ':' in name else None
                
                # Совпадение по имени и тегу
                if model_base == name_base:
                    if model_tag is None or model_tag == name_tag:
                        model_found = True
                        break
            
            if model_found:
                print_status(f"Модель {model_name} найдена", "✅")
                return True
            else:
                print_status(f"Модель {model_name} не найдена в списке", "⚠️")
                print_status("Продолжаем работу (модель загрузится при запросе)", "💡")
                return True  # Не блокируем запуск!
            
        except Exception as e:
            print_status(f"Ошибка проверки модели: {str(e)}", "⚠️")
            print_status("Продолжаем работу (модель загрузится при запросе)", "💡")
            return True  # Не блокируем запуск!
    
    def test_connection(self) -> bool:
        """Тестирует подключение к Ollama простым запросом"""
        try:
            import ollama
            
            print_status("Тестовый запрос к модели...", "🧪")
            
            response = ollama.chat(
                model=self._get_first_available_model(),
                messages=[{'role': 'user', 'content': 'Hi'}],
                options={'num_predict': 5}
            )
            
            if response and response.get('message'):
                print_status("Соединение с Ollama работает", "✅")
                return True
            return False
            
        except Exception as e:
            print_status(f"Тест соединения не прошёл: {str(e)}", "⚠️")
            return True  # Не блокируем
    
    def _get_first_available_model(self) -> str:
        """Получает имя первой доступной модели"""
        try:
            import ollama
            models_response = ollama.list()
            
            model_list = []
            if hasattr(models_response, 'models'):
                model_list = models_response.models
            elif isinstance(models_response, dict) and 'models' in models_response:
                model_list = models_response['models']
            
            for model in model_list:
                if hasattr(model, 'model'):
                    return model.model
                elif hasattr(model, 'name'):
                    return model.name
                elif isinstance(model, dict) and 'model' in model:
                    return model['model']
                elif isinstance(model, dict) and 'name' in model:
                    return model['name']
            
            return "qwen3.5:9b"  # default
        except:
            return "qwen3.5:9b"
