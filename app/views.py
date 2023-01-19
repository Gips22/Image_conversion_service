import asyncio

import aiohttp
import aiohttp_jinja2
from aiohttp import web
import io
import PIL.Image
import redis
from celery_config import delete_image, app_celery
from celery import Celery
from celery.worker import worker
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor

# app_celery = Celery('tasks', broker='redis://localhost:6379/0')
# app_celery.worker_main(['worker', '--loglevel=info', '--queues=tasks'])
r = redis.Redis()


# @app_celery.task
# def delete_image(key):
#     """Celery функция для удаления картинок либо после того, как пользователь скачал,
#     либо через сутки. Проверка в БД Redis"""
#     # if r.get(f"download:{key}"):
#         # проверка, скачал ли пользователь файл
#     print("call function delete")
#     try:
#         r.delete(f"image:{key}")
#         r.delete(f"image_converted:{key}")
#         r.delete(f"download:{key}")
#     except Exception as ex:
#         print(ex)

    # else:
    #     # если не скачал, удаляем через сутки
    #     r.expire(f"image:{key}", 86400)
    #     r.expire(f"image_converted:{key}", 86400)
    #     r.expire(f"download:{key}", 86400)


@aiohttp_jinja2.template("index.html")
async def index(request: web.Request) -> web.Response:
    return {'title': 'sdfsdf'}


async def download(request):
    """Функция обрабатывающая роут, отвечающий за скачивание файла"""
    key = request.match_info["key"]
    print(key)
    img_bytes = r.get(f"image_converted:{key}")
    if not img_bytes:
        raise aiohttp.web.HTTPNotFound()
    r.incr(f"download:{key}")
    delete_image.apply_async((key,), countdown=1)
    return aiohttp.web.Response(
        body=img_bytes,
        headers={
            "Content-Disposition": "attachment; filename=converted.jpeg",
            "Content-type": "image/jpeg",
        },
    )


async def handle(request):
    """Функция для обработки веб-сокет соединения"""
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.BINARY:
            img_bytes = msg.data
            image = PIL.Image.open(io.BytesIO(img_bytes))
            if image.format != "PNG":
                await ws.send_str("Неправильный формат загруженного изображения. Поддерживается только PNG.")
                continue
            key = r.incr("image_id")  # увеличиваем счетчик скаченных изображений
            r.set(f"image:{key}", img_bytes)
            await ws.send_str("Изображение загружено.")
            image_converted = image.convert("RGB")
            buffer = io.BytesIO()
            image_converted.save(buffer, format="JPEG")
            img_bytes_converted = buffer.getvalue()
            r.set(f"image_converted:{key}", img_bytes_converted)
            url = f"/download/{key}"
            await asyncio.sleep(1)
            await ws.send_str(f"Конвертированное изображение доступно по ссылке: {url}")
            executor = ProcessPoolExecutor()
            executor.submit(delete_image.delay, key)

            delete_image.apply_async((key,), countdown=86400)
            r.set(f"download:{key}", 1)
        return ws


"""если прользователь тскачал-сделать событие-проверять"""
