# Scrape licenses from Energy Regulatory Office

Scraping of [licenses](http://licence.eru.cz/) and data about [license holders](https://www.eru.cz/licence/informace-o-drzitelich) and learning working with Scrapy.


## Use

### Licenses

Initial placeholder spider partially scraping data from licenses for electricity generation. Output is best in json as some fields are lists of other items (e.g. one license can have multiple capacities).

`scrapy crawl electricitygen -O electricity.json`

### Holders

Complete spider scraping xml files about license holders (for any business like electricity generation, heat generation or gas distribution).

`scrapy crawl holders -O holders.csv`

## Test

`python -m pytest tests/`
