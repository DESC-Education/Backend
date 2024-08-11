FROM python:3.11.4-alpine

WORKDIR /usr/src/app



ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN pip install --upgrade pip
COPY requirements.txt /usr/src/app/requirements.txt
#COPY app/.env /usr/src/app/.env
RUN pip install -r requirements.txt




COPY DESC_Education /usr/src/app/






CMD python manage.py makemigrations \
    && python manage.py migrate \
    && python manage.py runserver 127.0.0.1:4000




EXPOSE 4000