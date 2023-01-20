from aiohttp import web

from views import index, handle, download


def setup_routes(app: web.Application):
    """Настраиваем пути, которые будут вести к нашей странице"""
    app.router.add_get("/", index)
    app.router.add_get('/convert', handle)  # роут для обработки веб-сокет соединения, отношения к url- не имеет
    app.router.add_get("/download/{key}", download)
