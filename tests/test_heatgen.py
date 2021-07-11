import pathlib

from scrapy.http import HtmlResponse

from licenses.spiders import heatgen


def test_parse_license():
    response = HtmlResponse(
        'https://domain.com/something?lic-id=310100053',
        body=pathlib.Path('tests/hlinsko.html').read_bytes(),
        )
    
    lic_list = list(heatgen.HeatGenSpider().parse(response))
    lic = lic_list[0]

    assert lic.id == '310100053'
    assert lic.pocet_zdroju == 11
    assert len(lic.vykony) == 5
    assert len(lic.provozovny) == 2

    assert lic.vykony[0].mw == 0.11
    assert lic.vykony[0].technologie == 'celkový'

    assert lic.vykony[-1].technologie == 'výkon kvet'
    assert lic.vykony[-1].druh == 'tepelný'
    assert lic.vykony[-1].mw == 2.1

    assert lic.provozovny[0].nazev == 'TEPLÁRENSKÁ SPOLEČNOST HLINSKO, spol. s r.o.'

    assert lic.provozovny[1].nazev == 'Kotelna ČSA'
    assert lic.provozovny[1].pocet_zdroju == 7

    assert lic.provozovny[1].vykony[-1].mw == 0.78
    assert len(lic.provozovny[1].vykony) == 2
