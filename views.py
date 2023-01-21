import io

import asyncio
import aiohttp
import aiohttp_jinja2
from aiohttp import web
from concurrent.futures import ProcessPoolExecutor

import PIL.Image
import redis

import celery_config
from tasks import delete_image



r = redis.Redis()


@aiohttp_jinja2.template("index.html")
async def index(request: web.Request) -> web.Response:
    return {'title': 'sdfsdf'}


delete_image.apply_async(args=[2], countdown=86400)


async def download(request):
    key = request.match_info["key"]
    img_bytes = r.get(f"image_converted:{key}")
    if not img_bytes:
        raise aiohttp.web.HTTPNotFound()
    r.incr(f"download:{key}")
    try:
        delete_image.apply_async(args=[key], countdown=86400)
    except Exception as ex:
        print(ex)
    return aiohttp.web.Response(
        body=img_bytes,
        headers={
            "Content-Disposition": "attachment; filename=converted.jpeg",
            "Content-type": "image/jpeg",
        },
    )


async def handle(request):
    """Function to handle websocket connection"""
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)
    while True:
        msg = await ws.receive()
        if msg.type == aiohttp.WSMsgType.BINARY:
            img_bytes = msg.data
            image = PIL.Image.open(io.BytesIO(img_bytes))
            if image.format != "PNG":
                await ws.send_str("Invalid image format. Only PNG is supported.")
                continue
            key = r.incr("image_id")  # increase counter for uploaded images
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
            print("after delete_im_apply")
            r.set(f"download:{key}", 1)
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' % ws.exception())
            break
    return ws



