FROM python:3.6

WORKDIR "/gtmhub_bot"

COPY . /gtmhub_bot

RUN pip install dialog-sdk-bot requests grpcio async_cron

CMD [ "python3", "/gtmhub_bot/gtmhub_bot.py" ]