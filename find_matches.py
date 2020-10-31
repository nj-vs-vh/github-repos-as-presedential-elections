import yaml
from collections import defaultdict
from typing import Dict, Tuple

from tqdm import tqdm

from utils import sorted_dict, trim_distribution_dict


ELECTIONS_FILE = 'data/election_results.yaml'

with open(ELECTIONS_FILE, 'r') as f:
    elections = yaml.safe_load(f)


REPOS_FILE = 'data/languages_in_repos.yaml'
with open(REPOS_FILE, 'r') as f:
    repos = yaml.safe_load(f)


dim_number = None
rounding = 0.0005


def results_tuple(d: Dict) -> Tuple[int]:
    trim_size = dim_number or len(d)
    if len(d) < trim_size:
        return None
    return tuple(
        round(v / rounding)
        for v in trim_distribution_dict(sorted_dict(d), size=trim_size).values()
    )


matches = defaultdict(lambda: ([], []))

for repo, langs in tqdm(repos.items()):
    res_tuple = results_tuple(langs)
    if res_tuple:
        matches[res_tuple][0].append('https://github.com/' + repo)

for page, election in tqdm(elections.items()):
    res_tuple = results_tuple(election['results'])
    if res_tuple:
        matches[res_tuple][1].append('https://en.wikipedia.org' + page)


results = [
    {'dimensions': dim_number, 'precentage rounding': 100 * rounding}
]
for vector, repo_elections in matches.items():
    if repo_elections[0] and repo_elections[1]:
        results.append(
            {
                'values': [value * rounding for value in vector],
                'repos': repo_elections[0],
                'elections': repo_elections[1]
            }
        )

with open('matches.yaml', 'w') as f:
    yaml.dump(results, f)
