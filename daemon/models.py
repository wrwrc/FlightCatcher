import sys
import time
from datetime import date, datetime
import mysql.connector


class MySqlConnection():
    def __init__(self, **settings):
        self.settings = settings

    def __enter__(self):
        self.conn = mysql.connector.connect(**self.settings)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cursor.close()
        self.conn.close()

    def execute(self, operation, params=None, multi=False):
        self.cursor.execute(operation, params, multi)
        self.conn.commit()

    def query(self, operation, params=None, multi=False):
        self.cursor.execute(operation, params, multi)
        return self.cursor.fetchall()

    def commit(self):
        self.conn.commit()

class Flight():
    def __init__(self, d):

        def getdatetime(
                item,
                fieldname,
                dformat = "%Y-%m-%dT%H:%M",
                default = None
                ):
            dt = None
            s = item.get(fieldname, default)
            if s:
                try:
                    dt = datetime.strptime(s, dformat)
                except ValueError:
                    pass

            return dt

        self.id = None
        self.flight_date = getdatetime(d, 'FlightDate', '%Y-%m-%d')

        if self.flight_date:
            self.flight_date = self.flight_date.date()

        self.flight_no = d.get('FlightNumber', None)
        self.airline_iata = d.get('AirlineID', None)
        self.route_type = d.get('AirRouteType', None)
        self.airport_dept = d.get('DepartureAirportID', None)
        self.airport_arr = d.get('ArrivalAirportID', None)
        self.sched_dept_time = getdatetime(d, 'ScheduleDepartureTime')
        self.actual_dept_time = getdatetime(d, 'ActualDepartureTime')
        self.est_dept_time = getdatetime(d, 'EstimatedDepartureTime')
        self.dept_remark = d.get('DepartureRemark', None)
        self.sched_arr_time = getdatetime(d, 'ScheduleArrivalTime')
        self.actual_arr_time = getdatetime(d, 'ActualArrivalTime')
        self.est_arr_time = getdatetime(d, 'EstimatedArrivalTime')
        self.arr_remark = d.get('ArrivalRemark', None)
        self.dept_terminal = d.get('DepartureTerminal', None)
        self.dept_gate = d.get('DepartureGate', None)
        self.arr_terminal = d.get('ArrivalTerminal', None)
        self.arr_gate = d.get('ArrivalGate', None)
        self.ac_type = d.get('AcType', None)
        self.baggage_claim = d.get('BaggageClaim', None)
        self.check_counter = d.get('CheckCounter', None)
        self.is_cargo = d.get('IsCargo', False)
        self.update_time = datetime.strptime(
            ''.join(d.get('UpdateTime', '').rsplit(':', 1)),
            "%Y-%m-%dT%H:%M:%S%z"
        )

    def isvalid(self):
        return self.flight_date and self.flight_no and self.airline_iata
