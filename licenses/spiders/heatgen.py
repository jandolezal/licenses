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

from licenses.items import HeatGenItem, CapacityItem, FacilityItem


def prepare_start_urls(
    base_url: str = "http://licence.eru.cz/detail.php?lic-id=",
    holders: str = "holders.json",
) -> List:
    """Prepare list of start urls from a json file with data about holders.

    First run `scrapy crawl holders -O holders.json` to obtain data about license holders
    to obtain license ids to construct start urls.

    Args:
        holders (str): JSON file with holders data. Defaults to 'holders.json'.

    Returns:
        List: List of urls for licenses for heat generation.
    """
    try:
        with open(holders) as json_file:
            json_content = json.load(json_file)
            return [
                base_url + row["id"] for row in json_content if row["predmet"] == "31"
            ]  # 31: výroba tepelné energie
    except FileNotFoundError:
        logging.critical(
            "File holders.json not found. Cannot build licenses urls to scrape."
        )
        return []


class HeatGenSpider(scrapy.Spider):
    """Spider to crawl licenses for heat generation (i.e. výroba tepelné energie)."""

    name = "heatgen"

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
    def _process_capacity_row(item, row_data):
        # Tři sloupce mají výkony
        if len(row_data) == 3:
            tech = row_data[0].strip().lower()

            try:
                el = float(row_data[1].replace(" ", ""))
                if el > 0:
                    item.vykony.append(
                        CapacityItem(druh="elektrický", technologie=tech, mw=el)
                    )
            except ValueError:
                pass
            try:
                tep = float(row_data[2].replace(" ", ""))
                if tep > 0:
                    item.vykony.append(
                        CapacityItem(druh="tepelný", technologie=tech, mw=tep)
                    )
            except ValueError:
                pass

        # Dva sloupce má Počet zdrojů, Řícní tok a Říční km
        elif len(row_data) == 2:
            if "počet zdrojů" in row_data[0].strip().lower():
                item.pocet_zdroju = int(row_data[1])

    def parse(self, response: scrapy.http.Response) -> HeatGenItem:
        """Parse license for heat generation.

        Page with license can have many capacities and many facilities and
        facilities can have many capacities (výkony).

        Args:
            response (scrapy.http.Response): Scrapy Response object.

        Yields:
            HeatGenItem: Item with scraped data for single license for heat generation.
        """
        lic_id = response.url[-9:]

        lic = HeatGenItem(id=lic_id)

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
            number = raw_number.split(" ")[-1]
            psc, obec, ulice, cp, okres, kraj = self._split_address(
                self._adjust_address(raw_address)
            )

            facility = FacilityItem(
                id=number,
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
                self._process_capacity_row(facility, row_data)

            lic.provozovny.append(facility)

        yield lic
