from celery import Celery
import redis
from app.views import r

app_celery = Celery('tasks', broker='redis://localhost:6379/0')


@app_celery.task
def delete_image(key):
    """Celery функция для удаления картинок либо после того, как пользователь скачал,
    либо через сутки. Проверка в БД Redis"""
    print("call function delete")
    try:
        r.delete(f"image:{key}")
        r.delete(f"image_converted:{key}")
        r.delete(f"download:{key}")
    except Exception as ex:
        print(ex)
