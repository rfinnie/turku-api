FROM python:3.10

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn .

USER nobody
ENV DJANGO_SETTINGS_MODULE="turku_api.settings"
ENV PYTHONPATH=/python/lib
CMD [ "gunicorn", "-b", "0.0.0.0:8000", "-k", "gthread", "turku_api.wsgi:application" ]
EXPOSE 8000/tcp
