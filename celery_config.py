"""Файл celery_config.py содержит конфигурацию для Celery приложения,
которое может быть использовано как worker."""
import redis
from celery import Celery

app_celery = Celery('tasks',
                    broker='redis://localhost:6379/0')  # создание ЭК Celery приложения с именем 'tasks' и настройкой брокера сообщений на Redis, который запущен на локальной машине по адресу localhost:6379/0.
app_celery.conf.beat_schedule = {}  # эта настройка нужна если нужно запускать задачу с периодичностью

r = redis.Redis()


@app_celery.task
def delete_image(key):
    print("function delete launched...")
    try:
        r.delete(f"image:{key}")
        r.delete(f"image_converted:{key}")
        r.delete(f"download:{key}")
    except Exception as ex:
        print(ex)
