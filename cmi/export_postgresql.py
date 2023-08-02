#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import datetime
import os
import psycopg

from cmi.extractor import Configuration, Extractor
from cmi.field import FieldType
from cmi.filter import Filter
from cmi.info_h import InfoH


def get_latest_event(database) -> list:
    cursor = database.cursor()
    cursor.execute('SELECT * FROM cmi ORDER BY time DESC LIMIT 1')
    result = cursor.fetchall()
    cursor.close()
    if len(result) == 0:
        return None
    return result[0]


def generate_sql(infoH: InfoH) -> str:
    columns = ['time']
    values = ['%s']
    for field in infoH.fields:
        if field.size == 0:
            continue

        if field.type == FieldType.ANALOG:
            columns.append(f'analog_{field.count:02}')
        else:
            columns.append(f'digital_{field.count:02}')
        values.append('%s')

    return f'INSERT INTO cmi ({", ".join(columns)}) VALUES({", ".join(values)}) ON CONFLICT (time) DO NOTHING;'


def main() -> None:
    now = datetime.date.today()
    parser = argparse.ArgumentParser(description='export data from C.M.I. to PostgreSQL', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--encoding', default='Windows-1252', type=str, help='file encoding')
    parser.add_argument('--host', default='cmi', type=str, help='C.M.I. hostname')
    parser.add_argument('--port', default=80, type=int, help='C.M.I. port')
    parser.add_argument('--user', default='winsol', type=str, help='Username to authenticate with')
    parser.add_argument('--password', default='data', type=str, help='Password to authenticate with')
    parser.add_argument('--after', default='1970-01-01', type=str, help='only import data that was created after (YYYY-MM-DD)')
    parser.add_argument('--before', default=now.strftime('%Y-%m-%d'), type=str, help='only import data that was created before (YYYY-MM-DD)')
    parser.add_argument('--unique', action=argparse.BooleanOptionalAction, help='only export events if any values have changed')
    parser.add_argument('--min-delta', default=1, type=int, help='minimum number of seconds between 2 events to configer both of them for export')
    parser.add_argument('--only-new', action=argparse.BooleanOptionalAction, help='only process events that are newer then the fewest own already in the database')
    parser.add_argument('--database', type=str, help='database connection string or set via CMI_DATABASE environment variable')

    arguments = parser.parse_args()
    before = datetime.datetime.fromisoformat(arguments.before).date()
    after = datetime.datetime.fromisoformat(arguments.after).date()
    delta = datetime.timedelta(seconds=arguments.min_delta)
    data = Extractor.process(Configuration(arguments.host, arguments.port, arguments.user, arguments.password, arguments.encoding, after, before, False))
    sql = generate_sql(data.infoH)
    expected_length = sql.count('%s')
    database = None
    try:
        connection = arguments.database
        if not connection:
            connection = os.getenv('CMI_DATABASE')
        database = psycopg.connect(connection)
        original = get_latest_event(database)
        inserts = []
        for group in data.groups:
            for event in group.events:
                values = [event.time]
                for value in event.values:
                    values.append(value.value)

                if len(values) != expected_length:
                    # incomplete dataset
                    continue
                if arguments.only_new and Filter.older(original, values):
                    continue
                if Filter.within_delta(original, values, delta):
                    continue
                if arguments.unique and not Filter.changed(original, values):
                    original = values
                    continue

                original = values
                inserts.append(values)

        cursor = database.cursor()
        cursor.executemany(sql, inserts)
        cursor.close()
        database.commit()
    finally:
        if database is not None:
            database.close()
    return


if __name__ == '__main__':
    main()
