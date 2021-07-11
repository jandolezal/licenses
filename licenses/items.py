# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html


from dataclasses import dataclass, field
from typing import List
from datetime import date


@dataclass
class HolderItem:
    """Represents a holder of a licence (držitel licence).

    id is a licence number (číslo licence) and not ičo (ic)
    because many of the holders are private citizens lacking ičo
    and many other details.
    """

    id: str
    version: int
    status: str
    ic: str
    nazev: str
    cislo_dom: str
    cislo_or: str
    ulice: str
    obec: str
    obec_cast: str
    psc: str
    okres: str
    kraj: str
    zeme: str
    den_opravneni: date
    den_zahajeni: date
    den_zaniku: date
    den_nabyti: date
    osoba: str
    predmet: str = None


@dataclass
class CapacityItem:
    """Represents capacity for license or facility."""

    druh: str
    technologie: str
    mw: float


@dataclass
class FacilityItem:
    """Represents facility listed on the license."""

    id: str
    nazev: str
    psc: str
    obec: str
    ulice: str
    cp: str
    okres: str
    kraj: str
    pocet_zdroju: int = None
    vykony: List[CapacityItem] = field(default_factory=list)


@dataclass
class ElectricityGenItem:
    """Represents one license for electricity generation."""

    id: str
    pocet_zdroju: int = None
    vykony: List[CapacityItem] = field(default_factory=list)
    provozovny: List[FacilityItem] = field(default_factory=list)


@dataclass
class HeatGenItem:
    """Represents one license for heat generation."""

    id: str
    pocet_zdroju: int = None
    vykony: List[CapacityItem] = field(default_factory=list)
    provozovny: List[FacilityItem] = field(default_factory=list)
