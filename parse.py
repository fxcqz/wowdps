import json
from tabulate import tabulate
from collections import defaultdict

def main():
    with open('data.json', 'r') as file:
        data = json.load(file)

    classes = defaultdict(list)
    for spec, ilvl, dps in data:
        if 343.0 <= ilvl <= 347.0:
            classes[spec].append(dps)

    final_data = {}
    for spec, dps_list in classes.items():
        final_data[spec] = sum(dps_list) / len(dps_list)

    sorted_data = [
        (class_, final_data[class_]) for class_ in
        sorted(final_data, key=final_data.get, reverse=True)
    ]

    print(tabulate(sorted_data, headers=('Spec', 'DPS')))

if __name__ == '__main__':
    main()
