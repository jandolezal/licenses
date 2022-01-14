import csv
import json
import pathlib
import sys


def main():

    business = sys.argv[1]

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
            writer.writerows(l)


if __name__ == '__main__':
    main()
