import csv
import dataclasses
import json
import pathlib
import sys


from licenses.items import HolderItem

def main():

    business = sys.argv[1]

    if business != 'drzitel':

        with pathlib.Path(f'data/{business}.json').open() as f:
            data = json.load(f)

        sources = []
        facilities = []
        capacities = []
        facility_capacities = []

        for item in data:

            for facility in item['provozovny']:
                new_facility = {}
                new_facility['cislo_licence'] = item['cislo_licence']
                new_facility['ev_cislo'] = facility['id']
                new_facility.update({k: v for k, v in facility.items() if k not in ('vykony', 'id')})
                facilities.append(new_facility)

                for capacity in facility['vykony']:

                    new_facility_capacity = {}
                    new_facility_capacity['cislo_licence'] = item['cislo_licence']
                    new_facility_capacity['ev_cislo'] = facility['id']
                    new_facility_capacity.update(capacity)
                    facility_capacities.append(new_facility_capacity)

            for capacity in item['vykony']:
                new_capacity = {}
                new_capacity['cislo_licence'] = item['cislo_licence']
                new_capacity.update(capacity)
                capacities.append(new_capacity)

            sources.append({'cislo_licence': item['cislo_licence'], 'pocet_zdroju': item['pocet_zdroju']})

        for filename, l in zip(
            ['zdroj_pocet.csv', 'vykon.csv', 'provozovna.csv', 'provozovna_vykon.csv'],
            [sources, capacities, facilities, facility_capacities],
        ):
            with pathlib.Path(f'data/{business}_{filename}').open('w') as f:
                writer = csv.DictWriter(f, fieldnames=list(l[0].keys()))
                writer.writeheader()
                l.sort(key=lambda x: x['cislo_licence'])
                writer.writerows(l)
    else:
        with pathlib.Path(f'data/{business}.csv').open(newline='') as fin:
            fieldnames = [field.name for field in dataclasses.fields(HolderItem)]
            reader = csv.DictReader(fin, fieldnames=fieldnames)
            l = [entry for entry in reader]
            with pathlib.Path(f'data/{business}.csv').open('w', newline='') as fout:
                writer = csv.DictWriter(fout, fieldnames=fieldnames)
                writer.writeheader()
                l.sort(key=lambda x: x['cislo_licence'])
                writer.writerows(l[:-1])


if __name__ == '__main__':
    main()
