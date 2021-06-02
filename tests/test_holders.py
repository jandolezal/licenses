from pathlib import Path
from datetime import date

from scrapy.http import HtmlResponse, XmlResponse

from licenses.spiders import holders


def test_parse():
    response = HtmlResponse(
        'https://domain.com/something',
        body=Path('tests/drzitele.html').read_bytes(),
        )
    
    xml_urls_list = list(holders.HoldersSpider().parse(response))

    first_url = xml_urls_list[0]
    assert first_url.url == 'https://www.eru.cz/documents/10540/2407284/LIC_11_2021-05-28-ver-1.xml/a1868a3b-ec72-44fc-bdda-561d6308fedc'

    last_url = xml_urls_list[-1]
    assert last_url.url == 'https://www.eru.cz/documents/10540/2407284/LIC_32_2021-05-28-ver-1.xml/a426f274-dde2-4c00-87de-0fa1e644337a'


def test_parse_license():
    response = XmlResponse(
        'https://www.domain.cz/LIC_31_2021-05-28-ver-1.xml',
        body=Path('tests/LIC_31_2021-05-28-ver-1.xml').read_bytes(),
        )

    heatgen_holders_list = list(holders.HoldersSpider().parse_xml(response))
    
    karlov = heatgen_holders_list[0]
    
    assert karlov.id == '310100016'
    assert karlov.version is None
    assert karlov.nazev == 'Obec Velký Karlov'
    assert karlov.ulice is None
    assert karlov.den_nabyti == date.fromisoformat('2001-08-10')
    assert karlov.osoba == 'Ing. Rostislav Lattner'
    assert karlov.predmet == '31'

    kasparova = heatgen_holders_list[-1]

    assert kasparova.id == '312136750'
    assert kasparova.predmet == '31'
