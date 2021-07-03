"""Spider for scraping licenses for electricity generation (i.e. výroba elektřiny).

Expects json file with metadata about holders scraped with holders spider.

One of this metadata, license id (číslo licence), is used to prepare list of start urls.
"""

import json

import pathlib
import scrapy
from typing import List, Union

from licenses.items import ElectricityGenItem, CapacityItem


def prepare_start_urls(
    base_url: str = 'http://licence.eru.cz/detail.php?lic-id=',
    holders: Union[str, pathlib.Path] = 'holders.json',
    ) -> List:
    """Prepare list of start urls from a json file with data about holders.

    First run `scrapy crawl holders -O holders.json` to obtain data about license holders
    to obtain license ids to construct start urls.

    Args:
        holders (Union[str, pathlib.Path], optional): [description]. Defaults to 'holders.json'.

    Returns:
        List: [description]
    """
    if not isinstance(holders, pathlib.Path):
        holders_path = pathlib.Path(holders)
    else:
        holders_path = holders

    with holders_path.open() as json_file:
        json_content = json.load(json_file)
        return [base_url + row['id'] for row in json_content if row['predmet'] == '11']  # 11: výroba elektřiny


class ElectricityGenSpider(scrapy.Spider):
    """Spider to crawl licenses for electricity generation (i.e. výroba elektřiny)."""

    name = 'electricitygen'

    start_urls = prepare_start_urls()

    def parse(self, response: scrapy.http.Response):
        """Parse license for electricity generation.

        TODO: Implement parsing facilities and their capacities. 
        Page with license can have many capacities and many facilities and
        facilities can have many capacities (výkony).

        Args:
            response (scrapy.http.Response): Scrapy Response object.

        Yields:
            ElectricityGenItem: Item with scraped data for single license for electricity generation.
        """
        lic_id = response.url[-9:]

        lic = ElectricityGenItem(id=lic_id)

        # Výkony za celou licenci (agregace za všechny provozovny)
        total_table = response.xpath('//table[@class="lic-tez-total-table"]/tr')

        for row in total_table[2:]:  # První dva řádky jsou hlavičky
            row_data = row.xpath('*/text()').getall()

            # Tři sloupce mají výkony
            if len(row_data) == 3:
                tech = row_data[0].strip().lower()

                try: 
                    el = float(row_data[1].replace(' ', ''))
                except ValueError:
                    el = None
                try: 
                    tep = float(row_data[2].replace(' ', ''))
                except ValueError:
                    tep = None

                if el and (el > 0):
                    el_cap = CapacityItem(druh='elektrický', technologie=tech, mw=el)
                    lic.vykony.append(el_cap)

                if tep and (tep > 0):
                    tep_cap = CapacityItem(druh='tepelný', technologie=tech, mw=tep)
                    lic.vykony.append(tep_cap)

            # Dva sloupce má Počet zdrojů, Řícní tok a Říční km
            elif len(row_data) == 2:
                if 'počet zdrojů' in row_data[0].strip().lower():
                    num = row_data[1]
                    lic.pocet_zdroju = int(num)

        yield lic
