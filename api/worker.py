from celery import Celery

app_celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')  # создание ЭК Celery приложения с именем 'tasks' и настройкой брокера сообщений на Redis, который запущен на локальной машине по адресу localhost:6379/0.

