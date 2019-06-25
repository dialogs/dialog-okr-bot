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

    def __init__(self, allowed_usernames, callback):
        threading.Thread.__init__(self)
        self.crons = {}
        self.allowed_usernames = allowed_usernames
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

    def is_valid_username(self, username):
        return username in self.allowed_usernames

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
        elif self.crons[peer_id].hour is None:
            if not GtmHubScheduler.is_valid_hour(value):
                raise InputException(_('Invalid hour'))
            self.crons[peer_id].hour = value
        else:
            if not self.is_valid_username(value):
                raise InputException(_('Invalid username\nAvailable usernames : {}').format('\n'+'\n'.join(self.allowed_usernames)))
            self.crons[peer_id].username = value

    def enable_cron(self, peer_id):
        day = int(self.crons[peer_id].day)
        hour = self.crons[peer_id].hour
        username = self.crons[peer_id].username

        job = CronJob(name=peer_id, loop=self.loop).weekday(day).at(hour).go(self.callback, peer_id, username)

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
        self.username = None

    def is_configured(self):
        return self.day is not None and self.hour is not None and self.username is not None
