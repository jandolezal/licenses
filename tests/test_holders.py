from pathlib import Path
from datetime import date

from scrapy.http import HtmlResponse, XmlResponse

from licenses.spiders import holder


def test_parse_license():
    response = XmlResponse(
        'https://www.domain.cz/LIC_31_2021-05-28-ver-1.xml',
        body=Path('tests/LIC_31_2021-05-28-ver-1.xml').read_bytes(),
    )

    heatgen_holders_list = list(holder.HoldersSpider().parse_xml(response))

    karlov = heatgen_holders_list[0]

    assert karlov.lic_id == 310100016
    assert karlov.verze is None
    assert karlov.nazev == 'Obec Velký Karlov'
    assert karlov.ulice is None
    assert karlov.den_nabyti == date.fromisoformat('2001-08-10')
    assert karlov.osoba == 'Ing. Rostislav Lattner'

    kasparova = heatgen_holders_list[-1]

    assert kasparova.lic_id == 312136750
