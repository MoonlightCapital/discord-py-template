FROM python:3.9

WORKDIR /usr/src/app

# For safety reason, create an user with lower privileges than root and run from there
RUN useradd -m -d /home/discordbot -s /bin/bash discordbot

RUN mkdir /usr/src/discordbot

RUN chown -R discordbot /usr/src/discordbot
USER discordbot

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "main.py" ]
