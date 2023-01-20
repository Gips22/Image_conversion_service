import aiohttp_jinja2
from aiohttp import web

import jinja2

routes = web.RouteTableDef()  # используется для создания и конфигурирования роутинга в aiohttp.
app = web.Application()  # экземпляр приложения aiohttp, который может использоваться для обработки запросов и маршрутизации.
                         # Этот экземпляр приложения может быть настроен с помощью различных мидлварей, роутов и т.д. и запущен с помощью функции run_app().


def setup_app(app):
    """Настройка всего приложения"""
    _setup_external_libraries(app)
    _setup_routes(app)


def _setup_routes(app):
    """Настройка роутов"""
    from routes import setup_routes
    setup_routes(app)


def _setup_external_libraries(application: web.Application) -> None:
    """Указываем шаблонизатору, что html-шаблоны надо искать в папке templates"""
    aiohttp_jinja2.setup(application, loader=jinja2.FileSystemLoader("templates"))


app = web.Application()  # создание веб сервера

if __name__ == "__main__":
    setup_app(app)  # настройка приложения
    web.run_app(app, host='0.0.0.0', port=8080)



"""
1. нужен ли jinja
2. отображение ссылки кликабельной в файле index.html
"""
