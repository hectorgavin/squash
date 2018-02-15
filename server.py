from datetime import datetime
from flask import Flask, jsonify
from squash2000 import Squash2000
from utils import date_range

app = Flask(__name__)


@app.route("/api/v1/timetables/<date>")
def get_timetable(date):
    return jsonify(Squash2000.get_timetable(datetime.strptime(date, '%Y-%m-%d').date()).as_dict())


@app.route("/api/v1/timetables/<from_date>/<to_date>")
def get_timetables(from_date, to_date):
    timetables = {}
    from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
    to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
    for current_date_obj in date_range(from_date_obj, to_date_obj):
        timetables[current_date_obj.strftime('%Y-%m-%d')] = Squash2000.get_timetable(current_date_obj).as_dict()
    return jsonify(timetables)


@app.route("/api/v1/courts/<date>")
def get_available_courts(date):
    return jsonify(Squash2000.get_timetable(datetime.strptime(date, '%Y-%m-%d').date()).get_available_courts())


@app.route("/api/v1/courts/<from_date>/<to_date>")
def get_available_courts_between_dates(from_date, to_date):
    timetables = {}
    from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
    to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
    for current_date_obj in date_range(from_date_obj, to_date_obj):
        timetables[current_date_obj.strftime('%Y-%m-%d')] = Squash2000.get_timetable(current_date_obj).get_available_courts()
    return jsonify(timetables)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
