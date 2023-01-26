"""Модуль тасков для celery worker"""
import redis
from loguru import logger
from celery import Celery

app_celery = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')  # создание ЭК Celery приложения с именем 'tasks' и настройкой брокера сообщений на Redis, который запущен на локальной машине по адресу localhost:6379/0.


logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB")
r = redis.Redis(host="redis", port=6379)


@app_celery.task(name='tasks.add')
def delete_image(key):
    logger.info("Начало работы функции delete_images...")
    if r.exists(f"image:{key}"):
        try:
            r.delete(f"image:{key}")
            r.delete(f"image_converted:{key}")
            r.delete(f"download:{key}")
        except Exception as ex:
            logger.error("Ошибка при удалении данных из БД", ex)
