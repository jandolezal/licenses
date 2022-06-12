from dataclasses import asdict
import logging
import sqlite3

from licenses.items import LicenseItem


class SqlitePipeline:

    def __init__(self, sqlite_uri):
        self.sqlite_uri = sqlite_uri

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            sqlite_uri=crawler.settings.get('SQLITE_URI'),
        )

    def open_spider(self, spider):
        self.con = sqlite3.connect(self.sqlite_uri)
        self.cur = self.con.cursor()
        self.cur.execute('create table if not exists zdroj (lic_id integer primary key, zdroju integer)')
        self.cur.execute('create table if not exists provozovna (lic_id integer, ev integer, nazev text, psc text, obec text, ulice text, cp text, okres text, kraj text, zdroju integer, primary key (lic_id, ev))')
        self.cur.execute('create table if not exists vykon (lic_id integer, druh text, technologie text, mw real)')
        self.cur.execute('create table if not exists provozovna_vykon (lic_id integer, ev integer, druh text, technologie text, mw real)')

    def close_spider(self, spider):
        self.con.commit()
        self.con.close()

    def process_item(self, item, spider):
        facilities = []
        for orig_fac in item.provozovny:
            fac = [v for k, v in asdict(orig_fac).items() if k != 'vykony']
            facilities.append(fac)
            try:
                self.cur.executemany("insert into provozovna_vykon values (?, ?, ?, ?, ?)", [list(asdict(vykon).values()) for vykon in orig_fac.vykony])
            except sqlite3.IntegrityError as e:
                logging.critical(e)
        try:
            self.cur.execute("insert into zdroj values (?, ?)", (item.lic_id, item.zdroju))
        except sqlite3.IntegrityError as e:
            logging.critical(e)
        try:
            self.cur.executemany("insert into provozovna values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", facilities)
        except sqlite3.IntegrityError as e:
            logging.critical(e)
        try:
            self.cur.executemany("insert into vykon values (?, ?, ?, ?)", [list(asdict(vykon).values()) for vykon in item.vykony] )
        except sqlite3.IntegrityError as e:
            logging.critical(e)
        return item
