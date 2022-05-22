import csv
from datetime import date
import pathlib
import re

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from scrapy.loader import ItemLoader

from licenses.items import HolderItem


BASE_URL = "https://www.eru.cz"


# Pomocné funkce pro čistění vstupních dat
def remove_fluff(x):
    if (x == "") or ("----" in x):
        return None
    return x


def convert_to_date(x):
    if not x:
        return None
    return date.fromisoformat(x)


def extract_business_code(url: str) -> str:
    """Extract code of the business type from the xml filename."""
    start = int(url.index("lic")) + 3
    end = start + 2
    predmet = url[start:end]
    return int(predmet)


class HolderLoader(ItemLoader):

    default_output_processor = TakeFirst()

    id_in = MapCompose(lambda x: int(x) if x else None)
    version_in = MapCompose(lambda x: int(x) if x else None)
    ic_in = MapCompose(remove_fluff)
    nazev_in = MapCompose(remove_fluff)
    cislo_dom_in = MapCompose(remove_fluff)
    cislo_or_in = MapCompose(remove_fluff)
    ulice_in = MapCompose(remove_fluff)
    obec_cast_in = MapCompose(remove_fluff)
    obec_in = MapCompose(remove_fluff)
    psc_in = MapCompose(remove_fluff)
    okres_in = MapCompose(remove_fluff)
    kraj_in = MapCompose(remove_fluff)
    zeme_in = MapCompose(remove_fluff)
    den_opravneni_in = MapCompose(convert_to_date)
    den_zahajeni_in = MapCompose(convert_to_date)
    den_zaniku_in = MapCompose(convert_to_date)
    den_nabyti_in = MapCompose(convert_to_date)
    osoba_in = MapCompose(lambda x: x if x else None)


class HoldersSpider(scrapy.Spider):
    name = "drzitel"

    start_urls = [
        BASE_URL + "/o-drzitelich-licence",
    ]


    def parse(self, response):
        """Retrieve link to newest article which contains links to xml files with data and yield request.
        """
        article_url = BASE_URL + response.xpath("//h3/span/a/@href").get()
        yield scrapy.Request(url=article_url, callback=self.parse_xml_links, encoding="utf-8")


    def parse_xml_links(self, response):
        """Parse initial page which contains list of links to xml files.
        Extract vocabulary of business types. Generate requests for these urls.
        """
        # Capture elements of interest from the page
        a_with_xml = response.xpath('//a[contains(@href, ".xml")]')

        # Get business types strings from filenames(urs)
        business_list = []
        xml_urls = []

        # Create vocabulary of codes and business descriptions and export them to csv
        for i, a in enumerate(a_with_xml):
            if i % 2 == 0: # there are two links to similar xml file. skip one of them
                xml_href = a.xpath('@href').get()
                code = extract_business_code(xml_href)
                description = a.xpath('text()').get().lower()
                # Gather list of business codes and the description
                business_list.append({"kod": code, "predmet": description})
                # Gather paths to the xml files
                xml_urls.append(BASE_URL + xml_href)

        # Save the businesses codes to a csv file
        pathlib.Path('data').mkdir(exist_ok=True)

        with pathlib.Path('data/druh.csv').open(mode='w') as csvf:
            writer = csv.DictWriter(csvf, fieldnames=["kod", "predmet"])
            writer.writeheader()
            business_list.sort(key=lambda x: x['kod'])
            writer.writerows(business_list)

        # Request xml files
        for url in xml_urls:
            yield scrapy.Request(url=url, callback=self.parse_xml, encoding="utf-8")

    def parse_xml(self, response):
        """Parse single xml file with actual data about license holders."""

        data_list = response.xpath("*")

        # Date of the file export is included in the filename
        file_date_string = re.search(r"\d{4}-\d{2}-\d{2}", response.url).group(0)
        pridano = convert_to_date(file_date_string)

        for data in data_list:

            data_dict = data.attrib

            l = HolderLoader(item=HolderItem())
            l.add_value("cislo_licence", data_dict["cislo_licence"])
            l.add_value("verze", data_dict["version"])
            l.add_value("status", data_dict["version_status"])
            l.add_value("ic", data_dict["subjekt_IC"])
            l.add_value("nazev", data_dict["subjekt_nazev"])
            l.add_value("cislo_dom", data_dict["subjekt_cislo_dom"])
            l.add_value("cislo_or", data_dict["subjekt_cislo_or"])
            l.add_value("ulice", data_dict["subjekt_ulice_nazev"])
            l.add_value("obec_cast", data_dict["subjekt_obec_cast"])
            l.add_value("obec", data_dict["subjekt_obec_nazev"])
            l.add_value("psc", data_dict["subjekt_PSC"])
            l.add_value("okres", data_dict["subjekt_okres"])
            l.add_value("kraj", data_dict["subjekt_kraj"])
            l.add_value("zeme", data_dict["subjekt_zeme"])
            l.add_value("den_opravneni", data_dict["subjekt_den_opravneni"])
            l.add_value("den_zahajeni", data_dict["subjekt_den_zahajeni"])
            l.add_value("den_zaniku", data_dict["subjekt_den_zaniku"])
            l.add_value("den_nabyti", data_dict["subjekt_den_nabyti_pravni_moci"])
            l.add_value("osoba", data_dict["odpovedny_zast"])

            yield l.load_item()
