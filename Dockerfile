FROM python:3.7

ENV LIBRARY_PATH=/lib:/usr/lib

WORKDIR "/tmp"

COPY . /tmp

RUN python3 -m pip install dialog-bot-sdk requests grpcio async_cron

CMD [ "python3", "/tmp/gtmhub_bot.py" ]
