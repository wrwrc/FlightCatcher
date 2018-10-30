import sys
from datetime import date, datetime, timezone
import logging
import config
from models import Flight, MySqlConnection

class TaskManager:
    interrupted = False

    def __init__(self, db, ptx_client):
        self.db = db
        self.ptx_client = ptx_client
        self.localtz = datetime.utcnow().astimezone().tzinfo
        self.cache = {}

    def __getid(self, typ, iata):
        if typ not in self.cache:
            self.cache[typ] = {}

        if iata in self.cache[typ]:
            id = self.cache[typ][iata]
        else:
            ids = self.db.query('select id from ' + typ + 's where iata=%s', (iata,))
            if not ids:
                return None

            id = ids[0][0]
            self.cache[typ][iata] = id

        return id

    def __insert_flight(self, flight):
        script = (
            'INSERT INTO flights '
            '(flight_date,flight_no,route_type,airline_id,airport_dept_id'
            ',airport_dest_id,sched_dept_time,actual_dept_time'
            ',est_dept_time,dept_remark,sched_arr_time,actual_arr_time'
            ',est_arr_time,arr_remark,dept_terminal,dept_gate'
            ',arr_terminal,arr_gate,ac_type,baggage_claim,check_counter'
            ',is_cargo,update_time) '
            'VALUES (%(flight_date)s,%(flight_no)s,%(route_type)s'
            ',%(airline_id)s,%(airport_dept_id)s,%(airport_dest_id)s'
            ',%(sched_dept_time)s,%(actual_dept_time)s,%(est_dept_time)s'
            ',%(dept_remark)s,%(sched_arr_time)s,%(actual_arr_time)s'
            ',%(est_arr_time)s,%(arr_remark)s,%(dept_terminal)s'
            ',%(dept_gate)s,%(arr_terminal)s,%(arr_gate)s,%(ac_type)s'
            ',%(baggage_claim)s,%(check_counter)s,%(is_cargo)s'
            ',%(update_time)s)'
        )

        flight.airline_id = self.__getid('airline', flight.airline_iata)
        if not flight.airline_id:
            return

        flight.airport_dept_id = self.__getid('airport', flight.airport_dept)
        flight.airport_dest_id = self.__getid('airport', flight.airport_arr)

        self.db.execute(script, vars(flight))

    def __update_flight(self, flight):
        script = (
            'update flights'
            '   set sched_dept_time=%(sched_dept_time)s'
            '      ,actual_dept_time=%(actual_dept_time)s'
            '      ,est_dept_time=%(est_dept_time)s'
            '      ,dept_remark=%(est_dept_time)s'
            '      ,sched_arr_time=%(sched_arr_time)s'
            '      ,actual_arr_time=%(actual_arr_time)s'
            '      ,est_arr_time=%(est_arr_time)s'
            '      ,arr_remark=%(arr_remark)s'
            '      ,dept_terminal=%(dept_terminal)s'
            '      ,dept_gate=%(dept_gate)s'
            '      ,arr_terminal=%(arr_terminal)s'
            '      ,arr_gate=%(arr_gate)s'
            '      ,baggage_claim=%(baggage_claim)s'
            '      ,check_counter=%(check_counter)s'
            '      ,update_time=%(update_time)s'
            ' where id=%(id)s'
        )

        self.db.execute(script, vars(flight))

    def __get_flight_update_time(self, f_date, f_no, a_iata):
        rows = self.db.query(
                'select f.id, f.update_time'
                '  from flights as f'
                '  join airlines as a on f.airline_id=a.id'
                ' where f.flight_date=%s and f.flight_no=%s and a.iata=%s'
                ' order by f.id'
                ' limit 1',
                (f_date, f_no, a_iata)
            )

        if rows:
            return {
                'id': rows[0][0],
                'update_time': rows[0][1].replace(tzinfo=self.localtz)
            }
        else:
            return None

    @staticmethod
    def __isascii(s):
        return len(s) == len(s.encode())

    def updateairports(self):
        if self.interrupted:
            return

        json = self.ptx_client.get('/v2/Air/Airport?$orderby=AirportID')

        if self.interrupted:
            return

        rows = self.db.query("select name_ch, name_en"
                        "      ,icao"
                        "      ,nationality"
                        "      ,iata"
                        "  from airports")
        rows = dict([(r[4], r) for r in rows])

        add_airport = (
            'INSERT INTO airports '
            '(name_ch, name_en, icao, nationality, iata) '
            'VALUES (%s, %s, %s, %s, %s);'
        )

        update_airport = (
            'UPDATE airports'
            '   SET name_ch=%s'
            '      ,name_en=%s'
            '      ,icao=%s'
            '      ,nationality=%s'
            ' WHERE iata=%s'
        )

        for item in json:
            iata = item.get('AirportIATA', None)
            if not iata:
                continue

            name = item.get('AirportName', {})
            name_ch = name.get('Zh_tw', None)
            name_en = name.get('En', None)

            icao = item.get('AirlineICAO', None)
            nation = item.get('AirlineNationality', None)

            if not name_en or self.__isascii(name_en):
                t = (name_ch, name_en, icao, nation, iata)
            elif not name_ch:
                t = (name_ch, None, icao, nation, iata)
            else:
                continue

            if self.interrupted:
                return

            row = rows.get(iata, None)
            if not row:
                rows[iata] = t
                self.db.execute(add_airport, t)
            elif t != row:
                rows[iata] = t
                self.db.execute(update_airport, t)

    def updateairlines(self):
        if self.interrupted:
            return

        json = self.ptx_client.get('/v2/Air/Airline')

        if self.interrupted:
            return

        rows = self.db.query("select name_ch, name_en"
                        "      ,alias_ch, alias_en"
                        "      ,icao"
                        "      ,email"
                        "      ,phone"
                        "      ,addr"
                        "      ,nationality"
                        "      ,iata"
                        "  from airlines")
        rows = dict([(r[9], r) for r in rows])

        add_airline = (
            'INSERT INTO airlines '
            '(name_ch, name_en, alias_ch, alias_en, icao, email, phone, addr, nationality, iata) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
        )

        update_airline = (
            'UPDATE airlines '
            'SET name_ch=%s, name_en=%s, '
            '    alias_ch=%s, aliax_en=%s, '
            '    icao=%s, '
            '    email=%s, '
            '    phone=%s, '
            '    addr=%s, '
            '    nationality=%s '
            'WHERE iata=%s'
        )

        for item in json:
            iata = item.get('AirlineIATA', None)
            if not iata:
                continue

            name = item.get('AirlineName', {})
            name_ch = name.get('Zh_tw', None)
            name_en = name.get('En', None)

            alias = item.get('AirlineNameAlias', {})
            alias_ch = alias.get('Zh_tw', None)
            alias_en = alias.get('En', None)

            icao = item.get('AirlineICAO', None)
            email = item.get('AirlineEmail', None)
            phone = item.get('AirlinePhone', None)
            addr = item.get('AirlineAddress', None)
            nation = item.get('AirlineNationality', None)

            if not name_en or self.__isascii(name_en):
                t = (name_ch, name_en, alias_ch, alias_en, icao, email, phone, addr, nation, iata)
            elif not name_ch:
                t = (name_ch, None, alias_ch, alias_en, icao, email, phone, addr, nation, iata)
            else:
                continue

            if self.interrupted:
                return

            row = rows.get(iata, None)
            if not row:
                self.db.execute(add_airline, t)
            elif t != row:
                self.db.execute(update_airline, t)

    def updateflights(self):
        if self.interrupted:
            return

        flight_list = self.ptx_client.get('/v2/Air/FIDS/Flight')

        if self.interrupted:
            return

        for data in flight_list:
            cur_flight = Flight(data)

            if not cur_flight.isvalid:
                continue

            if self.interrupted:
                return

            old_flight = self.__get_flight_update_time(
                    cur_flight.flight_date,
                    cur_flight.flight_no,
                    cur_flight.airline_iata
                )

            if self.interrupted:
                return

            if old_flight:
                if old_flight['update_time'] < cur_flight.update_time:
                    self.__update_flight(cur_flight)
            else:
                self.__insert_flight(cur_flight)

    def interrupt(self):
        self.interrupted = True