FROM python:3.8-slim

WORKDIR /app

ADD requirements.txt .

RUN pip install -r requirements.txt

RUN pip install gunicorn

COPY . .

EXPOSE 5000

CMD ["python3", "-u", "/app/application.py"]

#CMD gunicorn -b :5000 -w 2 --access-logfile - --error-logfile - application:app