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
            raise Exception('GtmHub error response "' + response.text + '" with code : ' + str(response.status_code))

        return response.json()

    def list_sessions(self):
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'gtmhub-accountId': self.account
        }
        response = requests.get(self.url + '/sessions', headers=headers)

        if response.status_code != 200:
            raise Exception('GtmHub error response "' + response.text + '"with code : ' + str(response.status_code))

        return response.json()

    def list_okr(self, list_id, user_id):
        query = {
            'includeMetrics': True,
            'ownerIds': user_id,
            'sessionId': list_id
        }
        headers = {
            'Authorization': 'Bearer '+self.token,
            'gtmhub-accountId': self.account
        }
        response = requests.get(self.url+'/goals', headers=headers, params=query)

        if response.status_code != 200:
            raise Exception('GtmHub error response "' + response.text + '"with code : ' + str(response.status_code))

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
            raise Exception('GtmHub error response "' + response.text + '"with code : ' + str(response.status_code))

        return response.json()

    def get_goal(self, goal_id):
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'gtmhub-accountId': self.account
        }
        response = requests.get(self.url + '/goals/' + goal_id, headers=headers)

        if response.status_code != 200:
            raise Exception('GtmHub error response "' + response.text + '"with code : ' + str(response.status_code))

        return response.json()

    def get_account(self, account_id):
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'gtmhub-accountId': self.account
        }
        response = requests.get(self.url + '/accounts/' + account_id, headers=headers)

        if response.status_code != 201:
            raise Exception('GtmHub error response "' + response.text + '"with code : ' + str(response.status_code))

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
            raise Exception('GtmHub error response "'+response.text+'"with code : '+str(response.status_code))

        return response.json()
