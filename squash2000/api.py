from datetime import datetime
import requests


class Squash2000Api(object):

    calendar_endpoint = 'http://www.squash2000-paramount-fitness.de/plan.php'

    @classmethod
    def get_timetable(cls, date=datetime.now().date()):
        response = requests.get(cls.calendar_endpoint + '?jahr={}&monat={}&tag={}'.format(date.year, date.month, date.day))
        if response.status_code == 200:
            return response.text
        else:
            raise Exception('There was an error fetching the Squash Calendar for {}'.format(date))