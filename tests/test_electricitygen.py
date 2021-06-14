from pathlib import Path

from scrapy.http import HtmlResponse

from licenses.spiders import electricitygen


def test_parse_license():
    response = HtmlResponse(
        'https://domain.com/something?lic-id=110100129',
        body=Path('tests/plzen.html').read_bytes(),
        )
    
    lic_list = list(electricitygen.ElectricityGenSpider().parse(response))
    lic = lic_list[0]

    assert lic.id == '110100129'
    assert lic.pocet_zdroju == 11
    assert len(lic.vykony) == 6

    assert lic.vykony[0].technologie == 'celkový'
    assert lic.vykony[0].mw == 274.190
    assert lic.vykony[1].mw == 725.825
    assert lic.vykony[1].druh ==  'tepelný'
    assert lic.vykony[1].technologie == 'celkový'

    assert lic.vykony[2].druh == 'elektrický'
    assert lic.vykony[3].technologie == 'parní'
    assert lic.vykony[2].mw == 254.5
    assert lic.vykony[3].mw == 725.640

    assert lic.vykony[5].technologie == 'plynový a spalovací'
    assert lic.vykony[4].mw == 19.690
    assert lic.vykony[5].mw == 0.185
