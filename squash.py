#!/usr/bin/python

import argparse
import time
from datetime import datetime

import requests
import yaml
from BeautifulSoup import BeautifulSoup

from utils import alert_osx, date_range, pretty_boolean, info, warn

squash_calendar_endpoint = 'http://www.squash2000-paramount-fitness.de/plan.php'


class Timetable(object):
    def __init__(self, html_str):
        self.timetable_map = self.build_timetable(html_str)

    def build_timetable(self, html_str):
        html = BeautifulSoup(html_str)

        # Find timetable table
        tables = html.findAll(name='table')
        calendar_table = None
        for table in tables:
            if table.find(name='center', text='Squash Belegungsplan'):
                calendar_table = table
                break
        if not calendar_table:
            raise Exception('Could not find timetable from response ' + html_str)

        # Get all "time" rows
        all_rows = calendar_table.findAll(name='tr')
        time_rows = []
        for row in all_rows:
            found = row.find(name='td', text='&nbsp;')
            if found:
                time_rows.append(row)

        # Build availability map
        timetable = {}
        for time_row in time_rows:
            key = time_row.find(name='td', attrs={'align': 'center'}).text
            courts_availability = [False, False, False, False, False]
            spots = []
            for td in time_row.findAll(name='td'):
                if td.text == '&nbsp;':
                    spots.append(td)
            for i in range(0, 5):
                if len(spots[i].attrs) == 1:
                    courts_availability[i] = spots[i].attrs[0][1] == 'background:#ffffff;'

            timetable[key] = courts_availability

        return timetable

    def get_available_times(self, time_filter=None):
        available = {}
        for time, courts in self.timetable_map.iteritems():
            if time_filter and time not in time_filter:
                continue
            for court in range(0, len(courts)):
                if courts[court]:
                    if time not in available:
                        available[time] = []
                    available[time].append(str(court+1))
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


def get_timetable_html(date):
    response = requests.get(squash_calendar_endpoint + '?jahr={}&monat={}&tag={}'.format(date.year, date.month, date.day))
    if response.status_code == 200:
        return response.text
    else:
        raise Exception('There was an error fetching the Squash Calendar for {}'.format(date))


if __name__ == '__main__':
    # Parse args
    parser = argparse.ArgumentParser(description='Squash Monitor 1.0')
    parser.add_argument('--from-date', help='Get available courts from the given date (i.e.: --from \'2018-01-01\'). Defaults to today')
    parser.add_argument('--to-date', help='Get available courts until the given date (i.e.: --to \'2018-01-01\'). Defaults to today')
    parser.add_argument('--monitor', help='Repeat process every x seconds until there is one court available (i.e.: --monitor 10)')
    parser.add_argument('--show-timetable', action='store_const', const=True, default=False, help='Display full timetable when there are available courts')
    args = parser.parse_args()

    from_date = datetime.now().date()
    to_date = from_date
    repeat_delay_seconds = None

    if args.from_date:
        from_date = datetime.strptime(args.from_date, '%Y-%m-%d').date()
    if args.to_date:
        to_date = datetime.strptime(args.to_date, '%Y-%m-%d').date()
    if args.monitor:
        repeat_delay_seconds = int(args.monitor)

    # Read config
    config = {
        'include': {
            'Monday': None,
            'Tuesday': None,
            'Wednesday': None,
            'Thursday': None,
            'Friday': None,
            'Saturday': None,
            'Sunday': None
        },
        'exclude': {
            'courts': [],
            'dates': []
        }
    }
    with open('squash.yaml', 'r') as config_file:
        config = yaml.load(config_file)

    # Get available courts
    while True:
        info('Checking available courts from {} to {}'.format(from_date.strftime('%B %d'), to_date.strftime('%B %d')))
        has_available_courts = False
        for current_date in date_range(from_date, to_date):
            day_name = current_date.strftime('%A')

            # Check if date should be ignored
            if day_name not in config['include'] or str(current_date) in config['exclude']['dates']:
                continue

            # Fetch timetable
            timetable = Timetable(get_timetable_html(current_date))
            available_times = timetable.get_available_times(time_filter=config['include'][day_name])

            # Check for available times/courts
            if available_times:
                filtered_available_times = {}
                for time, courts in available_times.iteritems():
                    filtered_available_times[time] = [court for court in available_times[time] if court not in config['exclude']['courts']]

                if filtered_available_times:
                    has_available_courts = True
                    print('')
                    print('# {}'.format(current_date.strftime('%A, %B %d')))

                    sorted_times = sorted(filtered_available_times.keys())
                    for time in sorted_times:
                        print('\t{}: {}'.format(time, ', '.join(filtered_available_times[time])))

                    if args.show_timetable:
                        print('')
                        print('Timetable for {}'.format(current_date.strftime('%B %d')))
                        print('')
                        timetable.pretty_print()

        # When monitoring, repeat until finding an available court
        if not repeat_delay_seconds:
            break
        elif has_available_courts:
            alert_osx('Some courts are available now')
            break
        else:
            warn('Sleeping for {} seconds...'.format(repeat_delay_seconds))
            time.sleep(repeat_delay_seconds)
