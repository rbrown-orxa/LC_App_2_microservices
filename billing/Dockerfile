FROM python:3.8

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY *.py ./

COPY config.ini .

CMD [ "python3", "./application.py"]
