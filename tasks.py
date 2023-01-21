import redis

from celery_config import app_celery

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
