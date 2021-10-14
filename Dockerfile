FROM python:3.9.6

RUN python3.9 -m pip install --upgrade pip \
    && mkdir /app

ADD . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

CMD python3 /app/app.py