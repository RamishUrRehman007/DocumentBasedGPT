FROM python:3.11-slim

WORKDIR /srv

COPY ./requirements.txt /srv/requirements.txt

RUN pip install -r /srv/requirements.txt

COPY ./ /srv/

CMD ["python", "backend/main.py"]
