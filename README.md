# Scrape licenses from Energy Regulatory Office

Python package build with Scrapy to get data about [licenses](http://licence.eru.cz/) and their [holders](https://www.eru.cz/licence/informace-o-drzitelich) from the Czech Energy Regulatory Office website.

There is a Datasette app [licence-eru](https://licence-eru.herokuapp.com/) hosted at Heroku with the final datasets (at the moment they are not updated regularly).


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
scrapy crawl drzitel -O data/drzitel.csv
```

### Licenses

Initial spiders `vyroba_elektriny` and `vyroba_tepla` partially scraping data from licenses for electricity generation and heat generation. Output is best in .json as some fields are lists of other items (one license can have many capacities and many facilities; facilities themselves can have many capacities).

Scraping data about land registry and in case of hydro power plants river and river km is not implemented.

These spiders depend on the licenses' numbers scraped by the `drzitel` spider for building urls to be scraped (filtering licenses numbers based on the business type, e.g. 11 for electricity generation or 31 for heat generation).

```bash
# Scrape electricity generation data
scrapy crawl vyroba_elektriny -O data/vyroba_elektriny.json

# Scrape heat generation data
scrapy crawl vyroba_tepla -O data/vyroba_tepla.json
```


```bash
# Convert .json files to few .csv files
python3 -m licenses.make_csvs vyroba_tepla

python3 -m licenses.make_csvs vyroba_elektriny

# Use csvs-to-sqlite to convert .csv files to sqlite database
csvs-to-sqlite data/*.csv licence.db

# Explore locally with Datasette
datasette licence.db

# Publish to Heroku with Datasette
datasette publish heroku licence.db -n licence-eru
```

## Test

```bash
python -m pytest tests/
```

## TODO

- Add GitHub workflow to scrape data on weekly basis
- Refactor without the .json step with a view of using Datasette (and .csv files)
- If possible take advantage of Scrapy features and remove standalone module `make_csvs`.
- Add spiders for other types of businesses (electricity trade, etc.)
