import sys
import logging

import mysql.connector

import config
from ptx import Client


class MySqlConnection(object):
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
        return self.cursor.execute(operation, params, multi)

    def query(self, operation, params=None, multi=False):
        self.cursor.execute(operation, params, multi)
        return self.cursor.fetchall()

    def commit(self):
        self.conn.commit()

isascii = lambda s: len(s) == len(s.encode())

def updateAirports(conn, ptx_client):
    json = ptx_client.get('/v2/Air/Airport')

    rows = conn.query("select name_ch, name_en"
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

        if not name_en or isascii(name_en):
            t = (name_ch, name_en, icao, nation, iata)
        elif not name_ch:
            t = (name_ch, None, icao, nation, iata)
        else:
            continue

        row = rows.get(iata, None)
        if not row:
            conn.execute(add_airport, t)
        elif t != row:
            conn.execute(update_airport, t)

    conn.commit()

def updateAirlines(conn, ptx_client):
    json = ptx_client.get('/v2/Air/Airline')

    rows = conn.query("select name_ch, name_en"
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

        if not name_en or isascii(name_en):
            t = (name_ch, name_en, alias_ch, alias_en, icao, email, phone, addr, nation, iata)
        elif not name_ch:
            t = (name_ch, None, alias_ch, alias_en, icao, email, phone, addr, nation, iata)
        else:
            continue

        row = rows.get(iata, None)
        if not row:
            conn.execute(add_airline, t)
        elif t != row:
            conn.execute(update_airline, t)

    conn.commit()

if __name__ == "__main__":
    logging.basicConfig(**config.LOG)

    try:
        client = Client(config.APP_ID, config.APP_KEY)
        with MySqlConnection(**config.DATABASE) as db:
            updateAirports(db, client)
            updateAirlines(db, client)
    except Exception as e:
        logging.exception("Error")


