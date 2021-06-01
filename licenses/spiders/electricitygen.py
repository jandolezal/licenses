import scrapy
from licenses.items import ElectricityGenItem, CapacityItem


class ElectricityGenSpider(scrapy.Spider):
    name = 'electricitygen'

    start_urls = [
        'http://licence.eru.cz/detail.php?lic-id=110100129',
        'http://licence.eru.cz/detail.php?lic-id=110100072',
        'http://licence.eru.cz/detail.php?lic-id=110100106',
        'http://licence.eru.cz/detail.php?lic-id=110100146',
    ]

    def parse(self, response):
        """Parse license.

        Page with license can have many capacities and many facilities.
        Facilities can have many capacities (výkony).
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
                    tep = float(row_data[1].replace(' ', ''))
                except ValueError:
                    tep = None

                if el and (el > 0):
                    el_cap = CapacityItem(druh='elektrický', technologie=tech, mw=el)
                    lic.vykony.append(el_cap)

                if tep and (tep > 0):
                    tep_cap = CapacityItem(druh='tepelný', technologie=tech, mw=el)
                    lic.vykony.append(tep_cap)

            # Dva sloupce má Počet zdrojů, Řícní tok a Říční km
            elif len(row_data) == 2:
                if 'počet zdrojů' in row_data[0].strip().lower():
                    num = row_data[1]
                    lic.pocet_zdroju = int(num)

        yield lic
