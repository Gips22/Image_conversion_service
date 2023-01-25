import io

import asyncio
import aiohttp
import aiohttp_jinja2
from aiohttp import web
import PIL.Image
import redis
from loguru import logger

from tasks import delete_image

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB")
r = redis.Redis()


@aiohttp_jinja2.template("index.html")
async def index(request: web.Request):
    """Асинхронная функция для обработки главного url. Использует шаблонизатор jinja."""
    return


@logger.catch
async def download(request):
    """Асинхронная функция вызываемая при скачивании изображения.
    Также запускает celery для удаления файлов из redis исходя из ТЗ."""
    key = request.match_info["key"]
    img_bytes = r.get(f"image_converted:{key}")
    if not img_bytes:
        raise aiohttp.web.HTTPNotFound()
    r.incr(f"download:{key}")
    delete_image.apply_async(args=[key], countdown=3)  # это task producer
    return aiohttp.web.Response(
        body=img_bytes,
        headers={
            "Content-Disposition": "attachment; filename=converted.jpeg",
            "Content-type": "image/jpeg",
        },
    )


@logger.catch
async def handle(request):
    """Функция для обработки веб-сокет соединения. Создается объект WebSocketResponse
    и ожидается входящий запрос. Если поступает в соединение изображение png- оно
    сохраняется в БД, конвертируется и сохраняется сконвертированный вариант.
    Далее запускается отложенная на сутки celery задача для удаления файлов из базы."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    while True:
        msg = await ws.receive()
        if msg.type == aiohttp.WSMsgType.BINARY:
            img_bytes = msg.data
            image = PIL.Image.open(io.BytesIO(img_bytes))
            if image.format != "PNG":
                await ws.send_str("Неверный формат. Поддерживается только PNG")
                continue
            key = r.incr("image_id")  # увеличиваем счетчик загруженных изображений
            r.set(f"image:{key}", img_bytes)
            await ws.send_str("Image uploaded.")
            image_converted = image.convert("RGB")
            buffer = io.BytesIO()
            image_converted.save(buffer, format="JPEG")
            img_bytes_converted = buffer.getvalue()
            r.set(f"image_converted:{key}", img_bytes_converted)
            url = f"/download/{key}"
            await asyncio.sleep(1)
            await ws.send_str(f"Converted image available at: {url}")
            delete_image.apply_async(args=[key], countdown=86400)
            r.set(f"download:{key}", 1)
        elif msg.type == aiohttp.WSMsgType.ERROR:
            logger.error('Веб-сокет соедиенние закрыто с ошибкой %s' % ws.exception())
            break
    return ws
