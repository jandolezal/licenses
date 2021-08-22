# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import dataclasses
import os

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

# Imports and models for database
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()

class Holder(Base):
    __tablename__ = 'holder'

    id = Column(Integer, primary_key=True)
    version = Column(Integer)
    status = Column(String)
    ic = Column(String)
    nazev = Column(String)
    cislo_dom = Column(String)
    cislo_or = Column(String)
    ulice = Column(String)
    obec = Column(String)
    obec_cast = Column(String)
    psc = Column(String)
    okres = Column(String)
    kraj = Column(String)
    zeme = Column(String)
    den_opravneni = Column(Date)
    den_zahajeni = Column(Date)
    den_zaniku = Column(Date)
    den_nabyti = Column(Date)
    osoba = Column(String)
    predmet = Column(String)
    pridano = Column(Date)

    def __repr__(self):
        return f"Holder(id={id}, name={nazev})"


class LicensesHoldersPipeline:
    """Pipeline for saving items to a Postgres database. Expects environment variable DATABASE_URL"""

    def open_spider(self, spider):
        database_url = os.getenv('DATABASE_URL')
        engine = create_engine(database_url)
        Base.metadata.create_all(engine, checkfirst=True)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()

        holder_item_dict = dataclasses.asdict(item)
        holder = Holder(**holder_item_dict)

        try:
            session.add(holder)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item
