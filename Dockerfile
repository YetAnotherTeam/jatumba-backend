FROM python:3.5

ENV PYTHONUNBUFFERED 1
RUN mkdir /jatumba-backend
COPY . /jatumba-backend
WORKDIR /jatumba-backend

RUN pip install pipenv && \
    pipenv install && \
    pipenv install gunicorn && \
    mkdir -p /var/log/gunicorn

CMD /root/.local/share/virtualenvs/jatumba-backend/bin/gunicorn \
    TPD.wsgi:application \
    --bind=:8000 \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log \
    --log-level debug

EXPOSE 8000
