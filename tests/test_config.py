import unittest
import json
import os

# with open('./config/config.json') as json_file:
#    return json.load(json_file)


class TestConfig(unittest.TestCase):

    TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(TESTS_DIR, os.pardir, 'config/config.json')
    CONFIG = {}

    def test_file_exist(self):
        self.assertTrue(os.path.exists(TestConfig.CONFIG_PATH))
        self.assertTrue(os.path.isfile(TestConfig.CONFIG_PATH))

    def test_file_is_json(self):
        with open(TestConfig.CONFIG_PATH) as config_file:
            TestConfig.CONFIG = json.load(config_file)

    def test_json_keys(self):
        self.assertTrue('dialogConfig' in TestConfig.CONFIG.keys())
        self.assertTrue('gtmhubConfig' in TestConfig.CONFIG.keys())

        self.assertTrue('host' in TestConfig.CONFIG['dialogConfig'].keys())
        self.assertTrue('port' in TestConfig.CONFIG['dialogConfig'].keys())
        self.assertTrue('token' in TestConfig.CONFIG['dialogConfig'].keys())

        self.assertTrue('url' in TestConfig.CONFIG['gtmhubConfig'].keys())
        self.assertTrue('token' in TestConfig.CONFIG['gtmhubConfig'].keys())
        self.assertTrue('account' in TestConfig.CONFIG['gtmhubConfig'].keys())
