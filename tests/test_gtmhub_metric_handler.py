import unittest
import json
import os

from src.input_exception import InputException
from src.gtmhub_metric_handler import GtmHubMetricHandler


class TestGtmhubMetricHandler(unittest.TestCase):

    TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(TESTS_DIR, os.pardir, 'config/config.json')

    with open(CONFIG_PATH) as json_file:
        CONFIG = json.load(json_file)

    CONFIG = CONFIG['gtmhubConfig']

    HANDLER = GtmHubMetricHandler(CONFIG['url'], CONFIG['token'], CONFIG['account'])

    def test_empty_instance(self):
        self.assertFalse(TestGtmhubMetricHandler.HANDLER.has_checkin(1))
        self.assertFalse(TestGtmhubMetricHandler.HANDLER.has_overview(1))
        self.assertEqual(TestGtmhubMetricHandler.HANDLER.get_bot_user_id(), '5d0b9a855888740001054d9d')
        self.assertEqual(TestGtmhubMetricHandler.HANDLER.get_list_id('Q2 2019'), '5d0b9a855888740001054d9f')
        self.assertEqual(TestGtmhubMetricHandler.HANDLER.get_user_id('tony tony'), '5d0b9a855888740001054d9d')

        with self.assertRaises(InputException):
            TestGtmhubMetricHandler.HANDLER.get_list_id('unknown')
        with self.assertRaises(InputException):
            TestGtmhubMetricHandler.HANDLER.get_user_id('unknown')
        with self.assertRaises(InputException):
            TestGtmhubMetricHandler.HANDLER.update_checkin(1, 'value')
        with self.assertRaises(InputException):
            TestGtmhubMetricHandler.HANDLER.cancel_checkin(1)
        with self.assertRaises(InputException):
            TestGtmhubMetricHandler.HANDLER.send_checkin(1)
        with self.assertRaises(InputException):
            TestGtmhubMetricHandler.HANDLER.cancel_overview(1)

        okrs = TestGtmhubMetricHandler.HANDLER.get_okr_list()

    def test_overview_checkin(self):
        TestGtmhubMetricHandler.HANDLER.create_overview(1)

        self.assertTrue(TestGtmhubMetricHandler.HANDLER.has_overview(1))
        self.assertTrue(TestGtmhubMetricHandler.HANDLER.is_in_overview(1, '5d0d9a6afd391a0001f7fb44'))
        self.assertFalse(TestGtmhubMetricHandler.HANDLER.is_in_overview(1, 'invalid_metric_id'))

        with self.assertRaises(InputException):
            TestGtmhubMetricHandler.HANDLER.create_overview(1)
        with self.assertRaises(InputException):
            TestGtmhubMetricHandler.HANDLER.create_checkin(1, 'invalid_metric_id')

        TestGtmhubMetricHandler.HANDLER.create_checkin(1, '5d0d9a405888740001055207')

        with self.assertRaises(InputException):
            TestGtmhubMetricHandler.HANDLER.update_checkin(1, 'not numeric')

        TestGtmhubMetricHandler.HANDLER.update_checkin(1, '35')  # was 32
        TestGtmhubMetricHandler.HANDLER.update_checkin(1, 'Just some text comment')

        with self.assertRaises(InputException):
            TestGtmhubMetricHandler.HANDLER.update_checkin(1, 'invalid confidence')

        TestGtmhubMetricHandler.HANDLER.update_checkin(1, '0.9')

        checkin_info = TestGtmhubMetricHandler.HANDLER.get_preview_info(1)

        self.assertEqual(checkin_info['new_percentage'], 11)

        TestGtmhubMetricHandler.HANDLER.cancel_checkin(1)

        TestGtmhubMetricHandler.HANDLER.cancel_overview(1)

        self.assertFalse(TestGtmhubMetricHandler.HANDLER.has_overview(1))

    def test_full_overview(self):
        overview_values = (
            ('35', 'Just a test comment', '0.7', 25),
            ('40', 'Just a test comment', '0.6', 50),
            ('57', 'Just a test comment', '0.8', 41),
            ('225', 'Just a test comment', '0.8', 47),
            ('9100', 'Just a test comment', '0.9', 60),
            ('2500', 'Just a test comment', '0.6', 14)
        )

        TestGtmhubMetricHandler.HANDLER.create_overview(1)

        for checkin_value in overview_values:
            metric_id = TestGtmhubMetricHandler.HANDLER.get_next_overview_checkin_id(1)
            TestGtmhubMetricHandler.HANDLER.create_checkin(1, metric_id)
            TestGtmhubMetricHandler.HANDLER.update_checkin(1, checkin_value[0])
            TestGtmhubMetricHandler.HANDLER.update_checkin(1, checkin_value[1])
            TestGtmhubMetricHandler.HANDLER.update_checkin(1, checkin_value[2])

            preview_info = TestGtmhubMetricHandler.HANDLER.get_preview_info(1)
            new_percent = preview_info['new_percentage']

            self.assertEqual(new_percent, checkin_value[3])

            TestGtmhubMetricHandler.HANDLER.send_checkin(1)

        self.assertEqual(TestGtmhubMetricHandler.HANDLER.get_overview_lenght(1), 0)
        TestGtmhubMetricHandler.HANDLER.cancel_overview(1)

    def test_reset_values(self):  # return the values to match on the next test execution
        overview_values = (
            ('22', 'Initial test value', '0.8', 3),
            ('19', 'Initial test value', '0.8', 20),
            ('32', 'Initial test value', '0.7', 7),
            ('199', 'Initial test value', '0.8', 20),
            ('9500', 'Initial test value', '0.8', 33),
            ('1200', 'Initial test value', '0.8', 7)
        )

        TestGtmhubMetricHandler.HANDLER.create_overview(1)

        for checkin_value in overview_values:
            metric_id = TestGtmhubMetricHandler.HANDLER.get_next_overview_checkin_id(1)
            TestGtmhubMetricHandler.HANDLER.create_checkin(1, metric_id)
            TestGtmhubMetricHandler.HANDLER.update_checkin(1, checkin_value[0])
            TestGtmhubMetricHandler.HANDLER.update_checkin(1, checkin_value[1])
            TestGtmhubMetricHandler.HANDLER.update_checkin(1, checkin_value[2])

            preview_info = TestGtmhubMetricHandler.HANDLER.get_preview_info(1)
            new_percent = preview_info['new_percentage']

            self.assertEqual(new_percent, checkin_value[3])

            TestGtmhubMetricHandler.HANDLER.send_checkin(1)

        self.assertEqual(TestGtmhubMetricHandler.HANDLER.get_overview_lenght(1), 0)
        TestGtmhubMetricHandler.HANDLER.cancel_overview(1)
