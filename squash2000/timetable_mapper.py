from BeautifulSoup import BeautifulSoup
from timetable import Timetable


class TimetableMapper(object):

    @staticmethod
    def to_timetable(timetable_html):
        html = BeautifulSoup(timetable_html)

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
                    courts_availability[i] = spots[i].attrs[0][1].strip() == 'background:#ffffff;'

            timetable[key] = courts_availability

        return Timetable(timetable)
