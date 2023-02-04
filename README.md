# Scrape licenses from Energy Regulatory Office

Python package written with Scrapy to get data about [licenses](http://licence.eru.cz/) for electricity and heat generation in Czechia and their [holders](https://www.eru.cz/o-drzitelich-licence) from the Czech Energy Regulatory Office website.

Little project which served as a playground for me to learn web scraping.

## Use

```bash
# Python and dependencies setup
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Holders

Complete spider scraping .xml files about license holders (for any business like electricity generation, heat generation or gas distribution). The business is encoded as first two digits of the license number.

```bash
# Scrape data about license holders
scrapy crawl holder
```

### Licenses

Initial spiders `electricitygen` and `heatgen` partially scraping data from licenses for electricity generation and heat generation.

Spiders use license ids to prepare links to scrape. Run `scrapy crawl holder` before these spiders.

River and river km is not scraped for the hydro power plants.

```bash
# Scrape electricity generation data
scrapy crawl electricitygen

# Scrape heat generation data
scrapy crawl heatgen
```

```bash
# Explore locally with Datasette
datasette licenses.db
```

## Test

```bash
python -m pytest tests/
```

## TODO

- Add spiders for other types of businesses (electricity trade, etc.)
