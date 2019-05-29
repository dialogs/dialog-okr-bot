from gtmhub_api import GtmHubApi
from gtmhub_checkin import GtmHubCheckin
from input_exception import InputException


class GtmHubMetricHandler:
    def __init__(self, api_url, api_token, api_account_id):
        self.api = GtmHubApi(api_url, api_token, api_account_id)
        self.checkins = {}
        self.users = self.api.list_users()['items']
        self.sessions = self.api.list_sessions()['items']
        self.bot_account_id = api_account_id
        self.bot_user_id = self.get_bot_user_id()

    def has_checkin(self, peer_id):
        return peer_id in self.checkins.keys()

    def get_bot_user_id(self):
        for user in self.users:
            if user['accountId'] == self.bot_account_id and user['type'] == 'user':
                return user['id']

    def get_user_id(self, username):
        available_usernames = ''
        for user in self.users:
            if user['type'] == 'user':
                available_usernames += '\n - '+user['name']
                if user['name'] == username:
                    return user['id']
        raise InputException('Invalid username\nAvailable usernames :'+available_usernames)

    def get_list_id(self, list_name):
        available_lists = ''
        for session in self.sessions:
            available_lists = '\n'+session['title']
            if session['title'] == list_name:
                return session['id']
        raise InputException('Invalid list name\nAvailable lists :'+available_lists)

    def get_okr_list(self, list_name, user_name):
        user_id = self.bot_account_id
        list_id = 'none'

        if user_name is not None:
            user_id = self.get_user_id(user_name)
        if list_name is not None:
            list_id = self.get_list_id(list_name)

        okr_list = self.api.list_okr(list_id, user_id)
        return okr_list['items']

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
            raise InputException('You have a checkin currently')

        metric = self.api.get_metric_with_goal(metric_id)

        self.checkins[peer_id] = GtmHubCheckin(metric)

    def update_checkin(self, peer_id, value):
        try:
            self.checkins[peer_id].set_value(value)
        except KeyError:
            raise InputException("You don't have a checkin currently")

    def cancel_checkin(self, peer_id):
        try:
            del self.checkins[peer_id]
        except KeyError:
            raise InputException("You don't have a checkin currently")

    def send_checkin(self, peer_id):
        try:
            update_info = self.checkins[peer_id].get_update_info()
            self.api.update_okr(update_info['id'], update_info['new_value'], update_info['comment'], update_info['confidence_level'])
            del self.checkins[peer_id]
        except KeyError:
            raise InputException("You don't have a checkin currently")

