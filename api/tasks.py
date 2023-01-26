"""Модуль тасков для celery worker"""
import redis
from loguru import logger

from celery_config import app_celery


logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB")
r = redis.Redis()


@app_celery.task
def delete_image(key):
    logger.info("Начало работы функции delete_images...")
    if r.exists(f"image:{key}"):
        try:
            r.delete(f"image:{key}")
            r.delete(f"image_converted:{key}")
            r.delete(f"download:{key}")
        except Exception as ex:
            logger.error("Ошибка при удалении данных из БД", ex)
