import yaml

from utils import sorted_dict, dict_to_dict_distance, trim_distribution_dict


ELECTIONS_FILE = 'data/election_results.yaml'

with open(ELECTIONS_FILE, 'r') as f:
    elections = yaml.safe_load(f)


REPOS_FILE = 'data/languages_in_repos.yaml'
with open(REPOS_FILE, 'r') as f:
    repos = yaml.safe_load(f)


def find_election_by_country_and_year(country, year):
    year = str(year)
    for election in elections.values():
        try:
            if election['country'] == country and election['year'] == year:
                return election
        except KeyError:
            pass
    else:
        return None


def find_closest_repo(election, trim_to_size=None):
    election_results = sorted_dict(election['results'])
    if trim_to_size:
        election_results = trim_distribution_dict(election_results, size=trim_to_size, others_key='Other candidates')

    election_size = len(election_results)

    closest_distance = 2
    for repo, langs in repos.items():
        if len(langs) < election_size:
            continue
        langs = sorted_dict(langs)
        langs = trim_distribution_dict(langs, size=election_size, others_key='Others')
        distance = dict_to_dict_distance(election_results, langs, 'Linf')
        if distance < closest_distance:
            closest_distance = distance
            closest_repo = repo
            closest_lang_trimmed = langs

    election_trimmed = election.copy()
    election_trimmed['results'] = election_results
    repo_trimmed = {'languages': closest_lang_trimmed, 'repo': closest_repo}
    return election_trimmed, repo_trimmed


el = find_election_by_country_and_year('Russia', 1991)
if not el:
    print('Not found :(')
    exit()

election, repo = find_closest_repo(el, trim_to_size=5)

with open('output.yaml', 'w') as f:
    yaml.dump([election, repo], f, sort_keys=False)
