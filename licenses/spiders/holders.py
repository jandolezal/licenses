from datetime import date

import scrapy
from licenses.items import HolderItem


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

        # Předmět podnikání z názvu souboru, např. 11 výroba elektřiny
        start = int(response.url.index("LIC_")) + 4
        end = start + 2
        predmet = response.url[start:end]

        # Pomocné funkce pro čistění vstupních dat
        def remove_fluff(x):
            if (x == "") or ("----" in x):
                return None
            return x

        convert_to_int = lambda x: int(x) if x else None
        convert_to_date = lambda x: date.fromisoformat(x) if x else None
        clean_person = lambda x: x if x else None

        for data in data_list:

            data_dict = data.attrib

            holder = HolderItem(
                id=data_dict["cislo_licence"],
                version=convert_to_int(data_dict["version"]),
                status=data_dict["version_status"],
                ic=remove_fluff(data_dict["subjekt_IC"]),
                nazev=remove_fluff(data_dict["subjekt_nazev"]),
                cislo_dom=remove_fluff(data_dict["subjekt_cislo_dom"]),
                cislo_or=remove_fluff(data_dict["subjekt_cislo_or"]),
                ulice=remove_fluff(data_dict["subjekt_ulice_nazev"]),
                obec_cast=remove_fluff(data_dict["subjekt_obec_cast"]),
                obec=remove_fluff(data_dict["subjekt_obec_nazev"]),
                psc=remove_fluff(data_dict["subjekt_PSC"]),
                okres=remove_fluff(data_dict["subjekt_okres"]),
                kraj=remove_fluff(data_dict["subjekt_kraj"]),
                zeme=remove_fluff(data_dict["subjekt_zeme"]),
                den_opravneni=convert_to_date(data_dict["subjekt_den_opravneni"]),
                den_zahajeni=convert_to_date(data_dict["subjekt_den_zahajeni"]),
                den_zaniku=convert_to_date(data_dict["subjekt_den_zaniku"]),
                den_nabyti=convert_to_date(data_dict["subjekt_den_nabyti_pravni_moci"]),
                osoba=clean_person(data_dict["odpovedny_zast"]),
                predmet=predmet,
            )

            yield holder
