FROM python:3.7

WORKDIR "/gtmhub_bot"

COPY . /gtmhub_bot

RUN python3 -m pip install dialog-bot-sdk requests grpcio async_cron

CMD [ "python3", "/gtmhub_bot/gtmhub_bot.py" ]
