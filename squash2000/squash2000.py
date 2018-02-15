from api import Squash2000Api
from timetable_mapper import TimetableMapper


class Squash2000(object):

    @staticmethod
    def get_timetable(date):
        return TimetableMapper.to_timetable(Squash2000Api.get_timetable(date))
