FROM python:3.11.4-alpine

WORKDIR /usr/src/app



ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN pip install --upgrade pip
COPY requirements.txt /usr/src/app/requirements.txt
#COPY app/.env /usr/src/app/.env
RUN pip install -r requirements.txt

COPY DESC_Education /usr/src/app/


COPY mediafiles /usr/src/mediafiles


CMD python manage.py makemigrations --noinput\
    && python manage.py migrate --noinput\
    && python manage.py collectstatic --noinput\
#    && python manage.py test\
#    && python manage.py runserver 0.0.0.0:4000
#    && gunicorn Settings.wsgi:application -c gunicorn_conf.py
    && python uvicorn_conf.py



EXPOSE 4000