#!/usr/bin/env python3
"""
Скрипт для локального запуска бота без Docker (для тестирования)
"""
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем и запускаем main
from main import main
import asyncio

if __name__ == '__main__':
    asyncio.run(main())
