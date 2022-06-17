from dataclasses import asdict
import datetime
import logging
import sqlite3

from scrapy.exceptions import CloseSpider

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
            self.cur.executemany("insert into provozovna_vykon values (?, ?, ?, ?, ?)", [list(asdict(vykon).values()) for vykon in orig_fac.vykony])
        
        self.cur.execute("insert into zdroj values (?, ?)", (item.lic_id, item.zdroju))
        self.cur.executemany("insert into provozovna values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", facilities)
        self.cur.executemany("insert into vykon values (?, ?, ?, ?)", [list(asdict(vykon).values()) for vykon in item.vykony] )
        return item


class HoldersSqlitePipeline:

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
        self.cur.execute('create table if not exists druh (kod integer primary key, predmet text)')
        self.cur.execute('create table if not exists drzitel (lic_id integer primary key, verze integer, status text, ic text, nazev text, cislo_dom text, cislo_or text, ulice text, obec text, obec_cast text, psc text, okres text, kraj text, zeme text, den_opravneni text, den_zahajeni text, den_zaniku text, den_nabyti text, osoba text, druh integer)')

    def close_spider(self, spider):
        self.con.commit()
        self.con.close()

    def process_item(self, item, spider):
        holder = [v if not isinstance(v, datetime.datetime) else v.isoformat() for v in asdict(item).values()]
        self.cur.execute("insert into drzitel values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", holder)
        return item
