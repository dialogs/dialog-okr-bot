from src.gtmhub_api import GtmHubApi
from src.gtmhub_checkin import GtmHubCheckin
from src.input_exception import InputException
from src.translator import _


class GtmHubMetricHandler:
    def __init__(self, api_url, api_token, api_account_id):
        self.api = GtmHubApi(api_url, api_token, api_account_id)
        self.checkins = {}
        self.overviews = {}
        self.users = self.api.list_users()['items']
        self.sessions = self.api.list_sessions()['items']
        self.bot_account_id = api_account_id
        self.bot_user_id = self.get_bot_user_id()

    def has_checkin(self, peer_id):
        return peer_id in self.checkins.keys()

    def has_overview(self, peer_id):
        return peer_id in self.overviews.keys()

    def is_in_overview(self, peer_id, metric_id):
        return (self.has_overview(peer_id)) and (metric_id in self.overviews[peer_id])

    def get_bot_user_id(self):
        for user in self.users:
            if user['accountId'] == self.bot_account_id and user['type'] == 'user':
                print(user['name'])
                return user['id']

    def get_usernames_list(self):
        usernames_list = []
        for user in self.users:
            if user['type'] == 'user':
                usernames_list.append(user['name'])
        return usernames_list

    def get_user_id(self, username):
        available_usernames = ''
        for user in self.users:
            if user['type'] == 'user':
                available_usernames += '\n - '+user['name']
                if user['name'] == username:
                    return user['id']
        raise InputException(_('Invalid username\nAvailable usernames : {}').format(available_usernames))

    def get_list_id(self, list_name):
        available_lists = ''
        for session in self.sessions:
            available_lists += '\n - '+session['title']
            if session['title'] == list_name:
                return session['id']
        raise InputException(_('Invalid list name\nAvailable lists : {}').format(available_lists))

    def get_okr_list(self, list_name=None, user_name=None):
        user_id = None
        list_id = None

        if user_name is not None:
            user_id = self.get_user_id(user_name)
        if list_name is not None:
            list_id = self.get_list_id(list_name)

        okr_by_project = self.api.list_okr(list_id, user_id)['items']
        okr_list = {}

        for okr in okr_by_project:
            if okr['metricsCount'] > 0:
                for metric in okr['metrics']:
                    if user_name is None or user_id == metric['ownerId']:
                        metric['project_name'] = okr['name']
                        metric['project_url'] = okr['url']
                        metric['project_attainment'] = okr['attainment']
                        okr_list[metric['id']] = metric

        return okr_list

    def get_next_overview_checkin_id(self, peer_id):
        if not self.has_overview(peer_id):
            raise InputException(_('You have not an overview currently'))
        if self.get_overview_lenght(peer_id) == 0:
            raise InputException(_('Your overview is currently empty'))
        return list(self.overviews[peer_id])[0]

    def get_overview_lenght(self, peer_id):
        if not self.has_overview(peer_id):
            return -1
        return len(self.overviews[peer_id])

    def get_okr_info(self, peer_id):
        return self.checkins[peer_id].get_okr_info()

    def get_confidence_levels(self, peer_id):
        return self.checkins[peer_id].get_confidence_levels()

    def get_preview_info(self, peer_id):
        return self.checkins[peer_id].get_preview_info()

    def get_checkin_state(self, peer_id):
        return self.checkins[peer_id].state

    def create_checkin(self, peer_id, metric_id):
        if self.has_checkin(peer_id):
            raise InputException(_('You have a checkin currently'))

        if self.has_overview(peer_id) and metric_id not in self.overviews[peer_id].keys():
            raise InputException(_("These OKR isn't in your current overview, please finish your overview before"))

        metric = self.api.get_metric_with_goal(metric_id)

        self.checkins[peer_id] = GtmHubCheckin(metric)

    def create_overview(self, peer_id, list_name=None, username=None):
        if self.has_checkin(peer_id):
            raise InputException(_('You have a checkin currently, please finish it before'))

        if self.has_overview(peer_id):
            raise InputException(_('You have a overview currently'))

        overview = self.get_okr_list(list_name, username)

        if len(overview) == 0:
            raise InputException(_("You have not OKR's to overview"))

        self.overviews[peer_id] = overview

    def update_checkin(self, peer_id, value):
        try:
            self.checkins[peer_id].set_value(value)
        except KeyError:
            raise InputException(_("You don't have a checkin currently"))

    def cancel_checkin(self, peer_id):
        try:
            del self.checkins[peer_id]
        except KeyError:
            raise InputException(_("You don't have a checkin currently"))

    def cancel_overview(self, peer_id):
        try:
            del self.overviews[peer_id]
        except KeyError:
            raise InputException(_("You don't have an overview currently"))

    def send_checkin(self, peer_id):
        try:
            update_info = self.checkins[peer_id].get_update_info()
            self.api.update_okr(update_info['id'], update_info['new_value'], update_info['comment'], update_info['confidence_level'])

            if self.has_overview(peer_id):
                del self.overviews[peer_id][update_info['id']]

            del self.checkins[peer_id]
        except KeyError:
            raise InputException(_("You don't have a checkin currently"))

