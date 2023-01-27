"""Модуль конфигурации celery"""
from celery import Celery


app_celery = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')  # создание ЭК Celery приложения с именем 'tasks' и настройкой брокера сообщений на Redis, который запущен на локальной машине по адресу localhost:6379/0.
app_celery.conf.beat_schedule = {}  # эта настройка нужна если нужно запускать задачу с периодичностью (celery beat)


