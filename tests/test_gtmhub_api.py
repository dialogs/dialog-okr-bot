import unittest
import json
import os

from src.gtmhub_api import GtmHubApi


class TestGtmhubApi(unittest.TestCase):

    TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(TESTS_DIR, os.pardir, 'config/config.json')

    with open(CONFIG_PATH) as json_file:
        CONFIG = json.load(json_file)

    CONFIG = CONFIG['gtmhubConfig']

    API = GtmHubApi(CONFIG['url'], CONFIG['token'], CONFIG['account'])

    def test_user_list(self):
        users = TestGtmhubApi.API.list_users()
        self.assertTrue('items' in users)
        self.assertTrue(len(users['items']) == 2)

    def test_sessions_list(self):
        sessions = TestGtmhubApi.API.list_sessions()
        self.assertTrue('items' in sessions)
        self.assertTrue(len(sessions['items']) == 2)

    def test_okr_list(self):
        own_id = '5d0b9a855888740001054d9d'
        boty_id = '5d10904a5888740001055320'
        q2_season_id = '5d0b9a855888740001054d9f'
        q3_season_id = '5d0d4195fd391a0001f7faa8'
        self.assertEqual(len(TestGtmhubApi.API.list_okr(None, own_id)['items']), 4)
        self.assertEqual(len(TestGtmhubApi.API.list_okr(q2_season_id, own_id)['items']), 3)
        self.assertEqual(len(TestGtmhubApi.API.list_okr(q3_season_id, own_id)['items']), 1)
        self.assertEqual(len(TestGtmhubApi.API.list_okr(None, boty_id)['items']), 1)
        self.assertEqual(len(TestGtmhubApi.API.list_okr(q2_season_id, boty_id)['items']), 1)
        self.assertEqual(len(TestGtmhubApi.API.list_okr(q3_season_id, boty_id)['items']), 0)

    def test_get_metric(self):
        metric = TestGtmhubApi.API.get_metric('5d0d9a6afd391a0001f7fb44')
        self.assertTrue('accountId' in metric)
        self.assertTrue('id' in metric)
        self.assertEqual(metric['accountId'], TestGtmhubApi.CONFIG['account'])

    def test_get_goal(self):
        goal = TestGtmhubApi.API.get_goal('5d0d4280fd391a0001f7faad')
        self.assertTrue('accountId' in goal)
        self.assertTrue('id' in goal)
        self.assertTrue('url' in goal)
        self.assertEqual(goal['accountId'], TestGtmhubApi.CONFIG['account'])

    def test_update_okr(self):
        metric = TestGtmhubApi.API.get_metric('5d0d9a6afd391a0001f7fb44')
        self.assertTrue('actual' in metric)
        self.assertTrue('confidence' in metric)
        self.assertTrue('value' in metric['confidence'])
        self.assertEqual(metric['actual'], 9500)
        self.assertEqual(metric['confidence']['value'], 0.8)
        result = TestGtmhubApi.API.update_okr('5d0d9a6afd391a0001f7fb44', 9250, 'Reduced for test', 0.9)
        self.assertTrue('value' in result)
        self.assertTrue('confidence' in result)
        self.assertEqual(result['value'], 9250)
        self.assertEqual(result['confidence'], 0.9)
        result = TestGtmhubApi.API.update_okr('5d0d9a6afd391a0001f7fb44', 9500, 'Returned to initial test values', 0.8)
        self.assertTrue('value' in result)
        self.assertTrue('confidence' in result)
        self.assertEqual(result['value'], 9500)
        self.assertEqual(result['confidence'], 0.8)
