from pathlib import Path
from datetime import date

from scrapy.http import HtmlResponse, XmlResponse

from licenses.spiders import holder


def test_parse():
    response = HtmlResponse(
        'https://domain.com/something',
        body=Path('tests/drzitele.html').read_bytes(),
    )

    xml_urls_list = list(holder.HoldersSpider().parse_xml_links(response))

    first_url = xml_urls_list[0]
    assert (
        first_url.url
        == 'https://www.eru.cz/sites/default/files/obsah/prilohy/lic112022-05-20-ver-1_0.xml'
    )

    last_url = xml_urls_list[-1]
    assert (
        last_url.url
        == 'https://www.eru.cz/sites/default/files/obsah/prilohy/lic322022-05-20-ver-1_0.xml'
    )


def test_parse_license():
    response = XmlResponse(
        'https://www.domain.cz/LIC_31_2021-05-28-ver-1.xml',
        body=Path('tests/LIC_31_2021-05-28-ver-1.xml').read_bytes(),
    )

    heatgen_holders_list = list(holder.HoldersSpider().parse_xml(response))

    karlov = heatgen_holders_list[0]

    assert karlov.lic_id == '310100016'
    assert karlov.verze is None
    assert karlov.nazev == 'Obec Velký Karlov'
    assert karlov.ulice is None
    assert karlov.den_nabyti == date.fromisoformat('2001-08-10')
    assert karlov.osoba == 'Ing. Rostislav Lattner'

    kasparova = heatgen_holders_list[-1]

    assert kasparova.lic_id == '312136750'
