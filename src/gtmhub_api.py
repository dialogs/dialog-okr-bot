from src.translator import _
import requests


class GtmHubApi:
    def __init__(self, url, token, account):
        self.url = url
        self.token = token
        self.account = account

    def list_users(self):
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'gtmhub-accountId': self.account
        }
        response = requests.get(self.url + '/assignees', headers=headers)

        if response.status_code != 200:
            raise Exception(_('GtmHub error response "{}" with code : {}').format(response.text, response.status_code))

        return response.json()

    def list_sessions(self):
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'gtmhub-accountId': self.account
        }
        response = requests.get(self.url + '/sessions', headers=headers)

        if response.status_code != 200:
            raise Exception(_('GtmHub error response "{}" with code : {}').format(response.text, response.status_code))

        return response.json()

    def list_okr(self, list_id, user_id):
        query = {
            'includeMetrics': True,
            'metricOwnerIds': user_id
        }
        headers = {
            'Authorization': 'Bearer '+self.token,
            'gtmhub-accountId': self.account
        }

        if list_id is not None:
            query['sessionId'] = list_id

        response = requests.get(self.url+'/goals', headers=headers, params=query)

        if response.status_code != 200:
            raise Exception(_('GtmHub error response "{}" with code : {}').format(response.text, response.status_code))

        return response.json()

    def get_metric_with_goal(self, metric_id):
        metric = self.get_metric(metric_id)
        goal = self.get_goal(metric['goalId'])
        metric['goal'] = goal
        return metric

    def get_metric(self, metric_id):
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'gtmhub-accountId': self.account
        }
        response = requests.get(self.url + '/metrics/' + metric_id, headers=headers)

        if response.status_code != 200:
            raise Exception(_('GtmHub error response "{}" with code : {}').format(response.text, response.status_code))

        return response.json()

    def get_goal(self, goal_id):
        query = {
            'fields': 'url'
        }
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'gtmhub-accountId': self.account
        }
        response = requests.get(self.url + '/goals/' + goal_id, headers=headers, params=query)

        if response.status_code != 200:
            raise Exception(_('GtmHub error response "{}" with code : {}').format(response.text, response.status_code))

        return response.json()

    def get_account(self, account_id):
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'gtmhub-accountId': self.account
        }
        response = requests.get(self.url + '/accounts/' + account_id, headers=headers)

        if response.status_code != 201:
            raise Exception(_('GtmHub error response "{}" with code : {}').format(response.text, response.status_code))

        return response.json()

    def update_okr(self, metric_id, new_value, comment, confidence_level):
        data = {
            'actual': new_value,
            'comment': comment,
            'confidence': confidence_level
        }
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'gtmhub-accountId': self.account
        }
        response = requests.post(self.url+'/metrics/'+metric_id+'/checkin', headers=headers, json=data)

        if response.status_code != 201:
            raise Exception(_('GtmHub error response "{}" with code : {}').format(response.text, response.status_code))

        return response.json()
