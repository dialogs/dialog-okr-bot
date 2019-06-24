import time
import asyncio
import threading
from async_cron.job import CronJob
from async_cron.schedule import Scheduler
from src.input_exception import InputException
from src.translator import _


def enum(**enums):
    return type('Enum', (), enums)


class GtmHubScheduler(threading.Thread):

    days_list = {
        '0': _('Monday'),
        '1': _('Tuesday'),
        '2': _('Wednesday'),
        '3': _('Thursday'),
        '4': _('Friday'),
        '5': _('Saturday'),
        '6': _('Sunday')
    }

    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.crons = {}
        self.callback = callback
        self.loop = asyncio.get_event_loop()
        self.scheduler = Scheduler(loop=self.loop)
        self.loop.create_task(self.scheduler.start())
        self.start()

    def run(self):
        self.loop.run_forever()

    @staticmethod
    def is_valid_day(day):
        return day in GtmHubScheduler.days_list.keys()

    @staticmethod
    def is_valid_hour(hour):
        try:
            time.strptime(hour, '%H:%M')
            return True
        except ValueError:
            return False

    def has_cron(self, peer_id):
        return peer_id in self.crons.keys()

    def need_params(self, peer_id):
        return self.has_cron(peer_id) and not self.crons[peer_id].is_configured()

    def create_cron(self, peer_id):
        if self.has_cron(peer_id):
            raise InputException(_('You have a reminder curently'))

        self.crons[peer_id] = Cron(peer_id)

    def set_value(self, peer_id, value):
        if not self.has_cron(peer_id):
            raise InputException(_('You have not a reminder to configure'))
        if self.crons[peer_id].is_configured():
            raise InputException(_('Your reminder is already configured'))
        if self.crons[peer_id].day is None:
            if not GtmHubScheduler.is_valid_day(value):
                raise InputException(_('Invalid day'))
            self.crons[peer_id].day = value
        else:
            if not GtmHubScheduler.is_valid_hour(value):
                raise InputException(_('Invalid hour'))
            self.crons[peer_id].hour = value

    def enable_cron(self, peer_id):
        day = int(self.crons[peer_id].day)
        hour = self.crons[peer_id].hour

        job = CronJob(name=peer_id, loop=self.loop).weekday(day).at(hour).go(self.callback, peer_id)

        self.scheduler.add_job(job)

    def cancel_cron(self, peer_id):
        try:
            self.scheduler.del_job(peer_id)
            del self.crons[peer_id]
        except KeyError:
            InputException(_("You don't have a reminder currently"))


class Cron:

    def __init__(self, peer_id):
        self.peer_id = peer_id
        self.day = None
        self.hour = None

    def is_configured(self):
        return self.day is not None and self.hour is not None
