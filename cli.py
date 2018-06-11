#!/usr/bin/python

import argparse
from time import time, sleep
from datetime import datetime

import yaml

from utils import alert_osx, date_range, info, warn
from squash2000 import Squash2000


def read_config():
    with open('config/config.yaml', 'r') as config_file:
		config = {
			'exclude': {
				'courts': [],
				'dates': []
			}
		}
		config_read = yaml.load(config_file)
		config['include'] = config_read['include']
		if config_read['exclude'] is not None:
			if config_read['exclude']['courts'] is not None:
				config['exclude']['courts'] = config_read['exclude']['courts']
			if config_read['exclude']['dates'] is not None:
				config['exclude']['dates'] = config_read['exclude']['dates']
		return config


if __name__ == '__main__':
    # Parse args
    parser = argparse.ArgumentParser(description='Squash2000 Court Checker 1.0')
    parser.add_argument('--from-date', help='Get available courts from the given date, including that day (i.e.: --from \'2018-01-01\'). Defaults to today')
    parser.add_argument('--to-date', help='Get available courts until the given date, including that day (i.e.: --to \'2018-01-01\'). Defaults to today')
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
    config = read_config()

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
            timetable = Squash2000.get_timetable(current_date)
            available_times = timetable.get_available_courts(time_filter=config['include'][day_name])

            # Check for available times/courts
            if available_times:
                filtered_available_times = {}
                for time, courts in available_times.iteritems():
                    filtered_available_times[time] = [str(court) for court in available_times[time] if str(court) not in config['exclude']['courts']]

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
            sleep(repeat_delay_seconds)
            config = read_config()
