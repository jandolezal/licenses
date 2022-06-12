"""Spider for scraping licenses for heat generation (i.e. výroba tepelné energie).

Expects json file with metadata about holders scraped with holders spider.

One of this metadata, license id (číslo licence), is used to prepare list of start urls.
"""

import json
import logging
import re
import sys
import unicodedata
import pathlib
from typing import List, Tuple

import scrapy

from licenses.items import LicenseItem, CapacityItem, FacilityItem, FacilityCapacityItem


def prepare_start_urls(
    base_url: str = "http://licence.eru.cz/detail.php?lic-id=",
    filepath: str = "data/drzitel.csv",
) -> List:
    """Prepare list of start urls from a json file with data about holders.

    First run e.g. `scrapy crawl holders -O data/drzitel.csv` to obtain data about license holders
    to obtain license ids to construct start urls.

    Args:
        filepath (str): CSV file with holders data. Defaults to 'data/drzitel.csv'.

    Returns:
        List: List of urls for licenses for heat generation.
    """
    try:
        with open(filepath) as file:
            return [
                base_url + line.split(',')[0] for line in file.readlines()[1:] if line.split(',')[0][:2] == '31'
            ]  # 31: výroba tepelné energie
    except FileNotFoundError:
        logging.critical("File {filepath} not found. Cannot build licenses urls to scrape.")
        return []


class HeatGenSpider(scrapy.Spider):
    """Spider to crawl licenses for heat generation (i.e. výroba tepelné energie)."""

    name = "vyroba_tepla"

    start_urls = prepare_start_urls()

    # Helper functions to parse address string
    @staticmethod
    def _adjust_address(address: str) -> List[str]:
        normalized = unicodedata.normalize("NFKC", address)
        adjusted = []
        for cast in normalized.split(","):
            adjusted.append(cast.strip())
        return adjusted

    @staticmethod
    def _split_address(address: List[str]) -> Tuple[str]:
        psc = address[0][:6].rstrip().replace(" ", "")
        obec = address[0][6:].strip()

        ulice_cp = address[1]
        re.search(re.compile("[0-9]+"), ulice_cp)
        match = re.search("[0-9]+/*[0-9]*", ulice_cp)
        if match:
            ulice = ulice_cp[: match.start() - 1]
            cp = match.group()
        else:
            ulice = ulice_cp
            cp = None

        okres = address[2].replace("okres ", "") if "okres" in address[2] else None
        try:
            kraj = address[3].replace("kraj ", "") if "kraj" in address[3] else None
        except IndexError:
            kraj = None

        return psc, obec, ulice, cp, okres, kraj

    @staticmethod
    def _process_capacity_row(entity, row_data, is_facility=False):
        # Tři sloupce mají výkony
        if len(row_data) == 3:
            tech = row_data[0].strip().lower()
            try:
                el = float(row_data[1].replace(" ", ""))
                if el > 0:
                    if is_facility:
                        entity.vykony.append(FacilityCapacityItem(lic_id=entity.lic_id, ev=entity.ev, druh="elektrický", technologie=tech, mw=el))
                    else:
                        entity.vykony.append(CapacityItem(lic_id=entity.lic_id, druh="elektrický", technologie=tech, mw=el))
            except ValueError:
                pass
            try:
                tep = float(row_data[2].replace(" ", ""))
                if tep > 0:
                    if is_facility:
                        entity.vykony.append(FacilityCapacityItem(lic_id=entity.lic_id, ev=entity.ev, druh="tepelný", technologie=tech, mw=tep))
                    else:
                        entity.vykony.append(CapacityItem(lic_id=entity.lic_id, druh="tepelný", technologie=tech, mw=tep))
            except ValueError:
                pass
        # Dva sloupce má Počet zdrojů, Řícní tok a Říční km
        elif len(row_data) == 2:
            if "počet zdrojů" in row_data[0].strip().lower():
                entity.zdroju = int(row_data[1])

    def parse(self, response: scrapy.http.Response) -> LicenseItem:
        """Parse license for heat generation.

        Page with license can have many capacities and many facilities and
        facilities can have many capacities (výkony).

        Args:
            response (scrapy.http.Response): Scrapy Response object.

        Yields:
            HeatGenItem: Item with scraped data for single license for heat generation.
        """
        lic_id = int(response.url[-9:])

        lic = LicenseItem(lic_id=lic_id)

        # Výkony za celou licenci (agregace za všechny provozovny)
        total_table = response.xpath('//table[@id="lic-tez-total-table"]/tr')

        for row in total_table[2:]:  # První dva řádky jsou hlavičky
            row_data = row.xpath("*/text()").getall()
            self._process_capacity_row(lic, row_data)

        # Data o jednotlivých provozovnách
        # Tabulka pro každou provozovnu a proměnné: název, adresa, katastr
        facilities_headers = response.xpath('//table[@class="lic-tez-header-table"]')
        # Tabulka s výkony pro každou provozovnu
        facilities_capacities = response.xpath('//table[@class="lic-tez-data-table"]')

        for header, capacity in zip(facilities_headers, facilities_capacities):

            # Zpracovat evidenční číslo, název a adresu provozovny
            raw_number, name, raw_address = header.xpath("tr/td/div/text()").getall()
            number = int(raw_number.split(" ")[-1])
            psc, obec, ulice, cp, okres, kraj = self._split_address(self._adjust_address(raw_address))

            facility = FacilityItem(
                lic_id=lic_id,
                ev=number,
                nazev=name,
                psc=psc,
                obec=obec,
                ulice=ulice,
                cp=cp,
                okres=okres,
                kraj=kraj,
            )

            # Zpracovat tabulku s výkony pro provozovnu
            for row in capacity.xpath("tr")[2:]:  # První dva řádky jsou hlavičky
                row_data = row.xpath("*/text()").getall()
                self._process_capacity_row(facility, row_data, is_facility=True)

            lic.provozovny.append(facility)

        yield lic
