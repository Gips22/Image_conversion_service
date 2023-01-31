FROM python:3.11

WORKDIR /api

COPY . .

RUN pip install --upgrade pip  \
    && pip install -r requirements.txt

CMD ["python", "main.py"]