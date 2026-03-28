# 🤖 YouTube AI Agent

Локальный ИИ-агент для анализа видео и каналов YouTube через Ollama. Работает полностью офлайн, без API ключей.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ollama](https://img.shields.io/badge/Ollama-qwen3.5:9b-green.svg)](https://ollama.com)

---

## ✨ Возможности

| Функция | Описание |
|---------|----------|
| 📹 **Анализ видео** | Саммари, ключевые тезисы, факты, цитаты |
| 🔍 **Поиск по каналу** | Поиск информации во всех видео канала |
| 📊 **3 уровня детализации** | Кратко / Стандартно / Максимально подробно |
| 💾 **Экспорт результатов** | TXT, Markdown, PDF |
| 🤖 **Полностью локально** | Без API ключей, данные не уходят в облако |
| ♻️ **Кэширование** | Повторная обработка не требуется |
| 📈 **Прогресс бар** | Видно статус каждого этапа обработки |

---

## 🚀 Быстрый старт (1 команда)

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/x001tk-Igor/Youtube-agent/main/install.sh | bash