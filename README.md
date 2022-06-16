# Scrape licenses from Energy Regulatory Office

Python package written with Scrapy to get data about [licenses](http://licence.eru.cz/) for electricity and heat generation in Czechia and their [holders](https://www.eru.cz/o-drzitelich-licence) from the Czech Energy Regulatory Office website.

Data are scraped every Friday and a Datasette app [licenses-ero](https://licenses-ero.herokuapp.com/) hosted at Heroku provides recent datasets.

It serves as a playground for me to learn web scraping.

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
# Two following spiders depend on licenses numbers scraped during this step into data/holder.csv file
scrapy crawl holder -O data/holder.csv

# Add license scope (electricity generation, heat generation, etc.) to the SQLite database
csvs-to-sqlite data/druh.csv
```

### Licenses

Initial spiders `electricitygen` and `heatgen` partially scraping data from licenses for electricity generation and heat generation.

The scrapers were first written with the assumption that Scrapy's .json [feed export](https://docs.scrapy.org/en/latest/topics/feed-exports.html) will be used. Output is best in .json as some fields are lists of other items (one license can have many capacities and many facilities; facilities themselves can have many capacities). Now, there is pipeline to save the data to several tables in SQLite database, but the .json step can still be used (although some columns are duplicated).

Scraping data about land registry and in case of hydro power plants river and river km is not implemented.

These spiders depend on the licenses' numbers scraped by the `holder` spider for building urls to be scraped (filtering licenses numbers based on the business type, e.g. 11 for electricity generation or 31 for heat generation).

```bash
# Scrape electricity generation data
scrapy crawl electricitygen

# There is a pipeline to save the data to SQLite database. Best feed output is to json (although some cols are duplicated)
scrapy crawl electricitygen -O data/electricitygen.json

# Scrape heat generation data
scrapy crawl heatgen
```

```bash
# Explore locally with Datasette
datasette licenses.db

# Publish to Heroku with Datasette
datasette publish heroku licenses.db -n licenses-ero
```

## Test

```bash
python -m pytest tests/
```

## TODO

- Add spiders for other types of businesses (electricity trade, etc.)
