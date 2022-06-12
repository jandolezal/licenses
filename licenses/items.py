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

    lic_id: int = field(default=None)
    verze: int = field(default=None)
    status: str = field(default=None)
    ic: str = field(default=None)
    nazev: str = field(default=None)
    cislo_dom: str = field(default=None)
    cislo_or: str = field(default=None)
    ulice: str = field(default=None)
    obec: str = field(default=None)
    obec_cast: str = field(default=None)
    psc: str = field(default=None)
    okres: str = field(default=None)
    kraj: str = field(default=None)
    zeme: str = field(default=None)
    den_opravneni: date = field(default=None)
    den_zahajeni: date = field(default=None)
    den_zaniku: date = field(default=None)
    den_nabyti: date = field(default=None)
    osoba: str = field(default=None)


@dataclass
class CapacityItem:
    """Represents capacity for license."""

    lic_id: int
    druh: str
    technologie: str
    mw: float


@dataclass
class FacilityCapacityItem:
    """Represents capacity for facility."""

    lic_id: int
    ev: int
    druh: str
    technologie: str
    mw: float


@dataclass
class FacilityItem:
    """Represents facility listed on the license."""
    
    lic_id: int
    ev: int
    nazev: str
    psc: str
    obec: str
    ulice: str
    cp: str
    okres: str
    kraj: str
    zdroju: int = None
    vykony: List[CapacityItem] = field(default_factory=list)


@dataclass
class LicenseItem:
    """Represents one license for electricity or heat generation."""

    lic_id: int
    zdroju: int = None
    vykony: List[CapacityItem] = field(default_factory=list)
    provozovny: List[FacilityItem] = field(default_factory=list)
