from utils.utils import pretty_boolean


class Timetable(object):

    def __init__(self, timetable_map={}):
        self.timetable_map = timetable_map

    def get_available_courts(self, time_filter=None):
        available = {}
        for time, courts in self.timetable_map.iteritems():
            if time_filter and time not in time_filter:
                continue
            for court in range(0, len(courts)):
                if courts[court]:
                    if time not in available:
                        available[time] = []
                    available[time].append(court+1)
        return available

    def pretty_print(self):
        print('Time/Court\t1\t2\t3\t4\t5')
        print('--------------------------------------------------')

        sorted_times = sorted(self.timetable_map.keys())

        for time in sorted_times:
            court_availability = self.timetable_map[time]
            print('{}\t\t{}\t{}\t{}\t{}\t{}'.format(
                time,
                pretty_boolean(court_availability[0]),
                pretty_boolean(court_availability[1]),
                pretty_boolean(court_availability[2]),
                pretty_boolean(court_availability[3]),
                pretty_boolean(court_availability[4])))
            print('--------------------------------------------------')

    def as_dict(self):
        result = {}
        for time, courts in self.timetable_map.iteritems():
            result[time] = {}
            for court in range(0, len(courts)):
                result[time][str(court+1)] = courts[court]
        return result
