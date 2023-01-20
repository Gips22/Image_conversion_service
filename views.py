import asyncio

import aiohttp
import aiohttp_jinja2
from aiohttp import web
import io
import PIL.Image
import redis
import celery_config
from celery_config import delete_image

r = redis.Redis()


@aiohttp_jinja2.template("index.html")
async def index(request: web.Request) -> web.Response:
    return {'title': 'sdfsdf'}


celery_config.delete_image.delay(1)
delete_image.apply_async(args=[2], countdown=86400)


async def download(request):
    key = request.match_info["key"]
    print(key)
    img_bytes = r.get(f"image_converted:{key}")
    if not img_bytes:
        raise aiohttp.web.HTTPNotFound()
    r.incr(f"download:{key}")
    celery_config.delete_image.delay(key)
    print('действие после delete_image')
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
            # executor = ProcessPoolExecutor()
            # executor.submit(delete_image.delay, key)
            #
            # delete_image.apply_async(args=[key], countdown=86400)
            r.set(f"download:{key}", 1)
        return ws
