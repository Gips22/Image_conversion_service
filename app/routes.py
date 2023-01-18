from app.views import index, handle
from aiohttp.abc import Application
import aiohttp



# настраиваем пути, которые будут вести к нашей странице
def setup_routes(app: Application):
    app.router.add_get("/", index)
    app.add_routes([aiohttp.web.get('/convert', handle)])
