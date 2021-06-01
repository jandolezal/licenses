# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html


from dataclasses import dataclass, field
from typing import List

@dataclass
class CapacityItem:

    druh: str
    technologie: str
    mw: float


@dataclass
class ElectricityGenItem:

    id: str
    pocet_zdroju: int = None
    vykony: List[CapacityItem] = field(default_factory=list)
