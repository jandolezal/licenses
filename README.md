# Scrape licenses from Energy Regulatory Office

Scraping of [licenses](http://licence.eru.cz/) and data about [license holders](https://www.eru.cz/licence/informace-o-drzitelich) and learning working with Scrapy.


## Use

### Holders

Complete spider scraping xml files about license holders (for any business like electricity generation, heat generation or gas distribution). The business is encoded as a first two digits in the license number.

```bash
# Scrape data about license holders
scrapy crawl drzitel -O data/drzitel.csv
```

### Licenses

Initial spiders partially scraping data from licenses for electricity generation and heat generation. Output is best in json as some fields are lists of other items (one license can have many capacities and many facilities; facilities themselves can have many capacities).

Scraping data about land registry and in case of hydro power plants river and river km is not implemented.

These spiders depend on the licenses' numbers scraped by the `drzitel` spider for building urls to be scraped (filtering licenses numbers based on the business type, e.g. 11 for electricity generation or 31 for heat generation).

```bash
# Scrape electricity generation data
scrapy crawl vyroba-elektriny -O data/vyroba_elektriny.json

# Scrape heat generation data
scrapy crawl vyroba_tepla -O data/vyroba_tepla.json
```


```bash
# Convert .json files to few .csv files
python3 -m licenses.make_csvs vyroba_tepla

python3 -m licenses.make_csvs vyroba_elektriny

# Use Datasette to convert .csv files to sqlite database
datasette data/*.csv licence.dbv

# Explore locally with Datasette
datasette licence.db
```

## Test

```bash
python -m pytest tests/
```
