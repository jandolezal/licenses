from datetime import date

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from scrapy.loader import ItemLoader

from licenses.items import HolderItem


# Pomocné funkce pro čistění vstupních dat
def remove_fluff(x):
    if (x == "") or ("----" in x):
        return None
    return x


def convert_to_date(x):
    if not x:
        return None
    return date.fromisoformat(x)


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
    name = "holders"

    start_urls = [
        "https://www.eru.cz/licence/informace-o-drzitelich",
    ]

    def parse(self, response):
        """Parse initial page which contains list of links to xml files.
        Generate requests for these urls.
        """

        # Get urls to xml files
        xml_urls = []
        xml_paras = response.xpath('//p[contains(text(), "XML")]/a/@href')
        for xml_href in xml_paras:
            xml_urls.append("https://www.eru.cz" + xml_href.get())

        for url in xml_urls:
            yield scrapy.Request(url=url, callback=self.parse_xml, encoding="utf-8")

    def parse_xml(self, response):
        """Parse xml file with actual data about license holders."""

        data_list = response.xpath("*")

        # Předmět podnikání z názvu xml souboru, např. 11 výroba elektřiny
        start = int(response.url.index("LIC_")) + 4
        end = start + 2
        predmet = response.url[start:end]

        for data in data_list:

            data_dict = data.attrib

            l = HolderLoader(item=HolderItem())
            l.add_value("id", data_dict["cislo_licence"])
            l.add_value("version", data_dict["version"])
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
            l.add_value("predmet", predmet)

            yield l.load_item()
