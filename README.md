# Scrape licenses from Energy Regulatory Office

Scraping of [licenses](http://licence.eru.cz/) and data about [license holders](https://www.eru.cz/licence/informace-o-drzitelich) and learning working with Scrapy.


## Use

### Holders

Complete spider scraping xml files about license holders (for any business like electricity generation, heat generation or gas distribution).

`scrapy crawl holders -O holders.csv`

### Licenses

Initial placeholder spiders partially scraping data from licenses for electricity generation and heat generation. Output is best in json as some fields are lists of other items (one license can have many capacities and many facilities; facilities themselves can have many capacities).

These spiders depend on the licenses numbers scraped by the `holders` spider for building urls to be scraped (filtering licenses numbers based on the business type, e.g. 11 for electricity generation or 31 for heat generation).

`scrapy crawl electricitygen -O electricitygen.json`

`scrapy crawl heatgen -O heatgen.json`


## Test

`python -m pytest tests/`
