import aiohttp_jinja2
from aiohttp import web
from main import routes

@aiohttp_jinja2.template("index.html")
async def index(request: web.Request) -> web.Response:
    """всю работу по формированию Http-ответа выполняет
     декоратор @aiohttp_jinja2.template("index.html") .
     Он получает данные из нашего View, которые мы возвращаем в виде словаря,
     находит шаблон index.html (о шаблонах написано ниже), подставляет туда данные
     из этого словаря, преобразует шаблон в html-текст и передает его в ответ на запрос."""
    return {'title': 'sdfsdf'}