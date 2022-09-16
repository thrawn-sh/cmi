#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import configparser
import datetime
import psycopg

from cmi.extractor import Configuration, Extractor
from cmi.field import FieldType
from cmi.info_h import InfoH


def get_database_connection(config, database: str):
    parameters = {}
    if config.has_section(database):
        for item in config.items(database):
            parameters[item[0]] = item[1]
    else:
        raise Exception(f'Section {database} not found in the {config} file')
    return psycopg.connect(**parameters)


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
    parser.add_argument('--database', default='postgresql', help='database config to use')
    parser.add_argument('--db-settings', default='database.ini', type=str, help='file containing postgresql connection configuration')

    arguments = parser.parse_args()
    before = datetime.datetime.fromisoformat(arguments.before).date()
    after = datetime.datetime.fromisoformat(arguments.after).date()
    config = configparser.ConfigParser()
    config.read(arguments.db_settings)
    data = Extractor.process(Configuration(arguments.host, arguments.port, arguments.user, arguments.password, arguments.encoding, after, before, False))

    sql = generate_sql(data.infoH)
    database = None
    try:
        database = get_database_connection(config, arguments.database)
        for group in data.groups:
            cursor = database.cursor()
            for event in group.events:
                values = [event.time]
                for value in event.values:
                    values.append(value.value)
                cursor.execute(sql, values)
            cursor.close()
            database.commit()
    finally:
        if database is not None:
            database.close()
    return


if __name__ == '__main__':
    main()