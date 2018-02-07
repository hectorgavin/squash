#!/usr/bin/python

import argparse
import requests
import yaml

from datetime import datetime, timedelta

from BeautifulSoup import BeautifulSoup

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

    def get_available_times(self, include=None):
        available = {}
        for time, courts in self.timetable_map.iteritems():
            if include and time not in include:
                continue
            for court in range(0, len(courts)):
                if courts[court]:
                    if time not in available:
                        available[time] = []
                    available[time].append(str(court+1))
        return available

    def yes_or_no(self, boolean):
        return 'Yes' if boolean else 'No'

    def pretty_print(self):
        print('Squash Belegungsplan')
        print('--------------------')
        print('')
        print('Time/Court\t1\t2\t3\t4\t5')

        sorted_times = sorted(self.timetable_map.keys())

        for time in sorted_times:
            court_availability = self.timetable_map[time]
            print('{}\t\t{}\t{}\t{}\t{}\t{}'.format(
                time,
                self.yes_or_no(court_availability[0]),
                self.yes_or_no(court_availability[1]),
                self.yes_or_no(court_availability[2]),
                self.yes_or_no(court_availability[3]),
                self.yes_or_no(court_availability[4])))


def get_timetable_html(date):
    response = requests.get(squash_calendar_endpoint + '?jahr={}&monat={}&tag={}'.format(date.year, date.month, date.day))
    if response.status_code == 200:
        return response.text
    else:
        raise Exception('There was an error fetching the Squash Calendar for year={}, month={}, day={}'.format(year, month, day))


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)+1):
        yield start_date + timedelta(n)


if __name__ == '__main__':
    # Parse args
    parser = argparse.ArgumentParser(description='Squash Monitor 1.0')
    parser.add_argument('--from-date', help='Get available courts from the given date (i.e.: --from \'2018-01-01\'). Defaults to today')
    parser.add_argument('--to-date', help='Get available courts until the given date (i.e.: --to \'2018-01-01\'). Defaults to today')
    args = parser.parse_args()

    from_date = datetime.now().date()
    to_date = from_date
    courts_set = {"1", "2", "3", "4", "5"}

    if args.from_date:
        from_date = datetime.strptime(args.from_date, '%Y-%m-%d').date()
    if args.to_date:
        to_date = datetime.strptime(args.to_date, '%Y-%m-%d').date()

    # Read config
    config = {
        'available': None,
        'courts': ["1", "2", "3", "4", "5"]
    }
    with open('squash.yaml', 'r') as config_file:
        config = yaml.load(config_file)
    exclude_courts = courts_set.difference(set(config['courts']))

    # Get available courts
    print('Available courts from {} to {}'.format(from_date.strftime('%B %d'), to_date.strftime('%B %d')))
    for current_date in daterange(from_date, to_date):
        day_name = current_date.strftime('%A')
        if config['available'] and day_name not in config['available']:
            continue

        timetable = Timetable(get_timetable_html(current_date))
        available_times = timetable.get_available_times(include=config['available'][day_name])

        if available_times:
            print('')
            print('# {}'.format(current_date.strftime('%A, %B %d')))

            sorted_times = sorted(available_times.keys())
            for time in sorted_times:
                courts = available_times[time]
                filtered_courts = [court for court in courts if court not in exclude_courts]
                print('\t{}: {}'.format(time, ', '.join(filtered_courts)))
