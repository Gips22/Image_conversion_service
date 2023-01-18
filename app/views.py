import asyncio

import aiohttp
import aiohttp_jinja2
from aiohttp import web
import io
import PIL.Image
import redis
from celery import Celery


app = Celery('tasks', broker='redis://localhost:6379/0')
r = redis.Redis()

@app.task
def delete_image(key):
    # проверка, скачал ли пользователь файл
    if r.get(f"download:{key}"):
        r.delete(f"image:{key}")
        r.delete(f"image_converted:{key}")
        r.delete(f"download:{key}")
    else:
        # если не скачал, удаляем через сутки
        r.expire(f"image:{key}", 86400)
        r.expire(f"image_converted:{key}", 86400)
        r.expire(f"download:{key}", 86400)


@aiohttp_jinja2.template("index.html")
async def index(request: web.Request) -> web.Response:
    return {'title': 'sdfsdf'}


async def handle(request):
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.BINARY:
            img_bytes = msg.data
            image = PIL.Image.open(io.BytesIO(img_bytes))
            if image.format != "PNG":
                await ws.send_str("Неправильный формат загруженного изображения. Поддерживается только PNG.")
                continue
            key = r.incr("image_id")
            r.set(f"image:{key}", img_bytes)
            await ws.send_str("Изображение загружено.")
            image_converted = image.convert("RGB")
            buffer = io.BytesIO()
            image_converted.save(buffer, format="JPEG")
            img_bytes_converted = buffer.getvalue()
            r.set(f"image_converted: {key}", img_bytes_converted)
            url = f"/download/{key}"
            await asyncio.sleep(7)
            await ws.send_str(f"Конвертированное изображение доступно по ссылке: {url}")
            delete_image.apply_async((key,), countdown=86400)
            r.set(f"download:{key}", 1)
        return ws
