#!/usr/bin/env python3
import ollama

print("🔍 Проверка структуры ollama.list()...")
models = ollama.list()
print(f"Тип ответа: {type(models)}")
print(f"Содержимое: {models}")

# Показываем имена моделей
if isinstance(models, dict):
    model_names = [m.get('name', '') for m in models.get('models', [])]
else:
    model_names = [str(m) for m in models]

print(f"\n✅ Найдено моделей: {len(model_names)}")
for name in model_names:
    print(f"   - {name}")
