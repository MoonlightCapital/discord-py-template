FROM python:3.9

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /app
WORKDIR /app

CMD [ "python3", "-u", "main.py" ]
