import yaml

import re


# shoutout to https://github.com/mledoze/countries
COUNTRIES_FILENAME = 'countries/dist/countries.yml'


with open(COUNTRIES_FILENAME, 'r') as f:
    countries_full_data = yaml.safe_load(f)

country_synonyms = dict()
for country in countries_full_data:
    name = country['name']
    official, common = name['official'].title(), name['common'].title()
    country_synonyms[official] = common
    country_synonyms[common] = common

del countries_full_data


country_matching_re = re.compile(r'\b' + '|'.join(f'({syn})' for syn in country_synonyms))


def get_common_name(synonym):
    return country_synonyms[synonym.title()]


__all__ = ['country_matching_re', 'get_common_name']
