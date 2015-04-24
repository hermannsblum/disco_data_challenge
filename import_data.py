import pandas as pd
import json


def import_businesses():
    businesses_file = 'data/yelp_academic_dataset_business.json'

    businesses_dict = []
    with open(businesses_file) as file:
        for line in file:
            businesses_dict.append(json.loads(line))

    businesses = pd.DataFrame(businesses_dict)
    return businesses

if __name__ == '__main__':
    businesses = import_businesses()
    print(list(businesses.columns.values))
