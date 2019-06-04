from input_exception import InputException
import re

def enum(**enums):
    return type('Enum', (), enums)


class GtmHubCheckin:
    STATES = enum(CREATED=0, INITIALIZED=1, COMMENTED=2, CONFIGURED=3)

    def __init__(self, metric_with_goal):
        self.id = metric_with_goal['id']
        self.title = metric_with_goal['name']
        self.current_value = metric_with_goal['actual']
        self.target_value = metric_with_goal['target']
        self.url = metric_with_goal['goal']['url']+'metric/'+metric_with_goal['id']+'/'

        self.current_confidence = 0.0

        if 'confidence' in metric_with_goal and 'value' in metric_with_goal['confidence']:
            self.current_confidence = metric_with_goal['confidence']['value']

        self.confidence_base_one = isinstance(self.current_confidence, float)

        self.state = GtmHubCheckin.STATES.CREATED
        self.new_value = None
        self.new_comment = None
        self.new_confidence = None

    def set_value(self, value):
        if self.state == GtmHubCheckin.STATES.CREATED:
            self.new_value = GtmHubCheckin.parse_numeric(value)
        elif self.state == GtmHubCheckin.STATES.INITIALIZED:
            GtmHubCheckin.parse_text(value)
            self.new_comment = value
        elif self.state == GtmHubCheckin.STATES.COMMENTED:
            self.new_confidence = self.parse_confidence(value)
        else:
            raise InputException('Checkin is already completed')

        self.state += 1

    @staticmethod
    def parse_numeric(value):
        try:
            return float(value)
        except ValueError:
            raise InputException('Invalid numeric value')

    @staticmethod
    def parse_text(value):
        if not value:
            raise InputException('Invalid empty text')
        return value

    def parse_confidence(self, value):
        try:
            if self.confidence_base_one:
                parsed_value = float(value)
            else:
                parsed_value = int(value)
            if parsed_value not in self.get_confidence_levels():
                raise Exception()
        except Exception:
            raise InputException('Invalid confidence level')
        return parsed_value

    def get_confidence_levels(self):
        confidence_levels = list(range(0, 11))
        if self.confidence_base_one:
            for key, value in enumerate(confidence_levels):
                confidence_levels[key] = value / 10
        return confidence_levels

    def get_okr_info(self):
        return {
            'title': self.title,
            'current_value': self.current_value,
            'target_value': self.target_value
        }

    def get_preview_info(self):
        return {
            'id': self.id,
            'title': self.title,
            'link': self.url,
            'new_percentage': round((self.new_value / self.target_value) * 100)
        }

    def get_update_info(self):
        return {
            'id': self.id,
            'new_value': self.new_value,
            'comment': self.new_comment,
            'confidence_level': self.new_confidence
        }