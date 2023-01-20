import jinja2
import aiohttp_jinja2

from aiohttp import web

routes = web.RouteTableDef()
app = web.Application()


def setup_routes(app):
    from routes import setup_routes
    setup_routes(app)


def setup_external_libraries(application: web.Application) -> None:
    """указываем шаблонизатору, что html-шаблоны надо искать в папке templates"""
    aiohttp_jinja2.setup(application, loader=jinja2.FileSystemLoader("templates"))


def setup_app(application):
    """настройка всего приложения"""
    setup_external_libraries(application)
    setup_routes(application)


app = web.Application()  # создание веб сервера


if __name__ == "__main__":
    setup_app(app)  # настройка приложения
    web.run_app(app, host='0.0.0.0', port=8080)

