from colors import color
from datetime import timedelta
from subprocess import check_call
import os


def date_range(start_date, end_date):
    for n in range(int ((end_date - start_date).days)+1):
        yield start_date + timedelta(n)


def alert_osx(message='Alert'):
    with open(os.devnull, 'w') as devnull:
        check_call(['/usr/bin/osascript', '-e', 'tell application (path to frontmost application as text) to display dialog "'+ message +'" buttons {"OK"} with icon stop'], stdout=devnull)


def yes_or_no(boolean):
    return 'Yes' if boolean else 'No'


def printc(string, the_color):
    print(color(string, fg=the_color))


def info(string):
    printc(string, 'green')


def warn(string):
    printc(string, 'yellow')


def error(string):
    printc(string, 'red')