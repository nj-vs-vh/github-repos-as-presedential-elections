import os

import requests
from requests.auth import HTTPBasicAuth

import yaml

from tqdm import tqdm


GITHUB_HEADER = {'Accept': 'application/vnd.github.v3+json'}

GITHUB_API_URL = 'https://api.github.com/'


github_auth_token = os.environ.get('GITHUB_TOKEN')


def get_repo_languages(owner, repo):
    url = GITHUB_API_URL + f'repos/{owner}/{repo}/languages'
    r = requests.get(url, headers=GITHUB_HEADER, auth=HTTPBasicAuth('nj-vs-vh', github_auth_token))
    try:
        languages = r.json()
        total = sum(languages.values())
        return {lang: score / total for lang, score in sorted(languages.items(), key=lambda item: item[1])}
    except Exception:
        return None


DATA_FOLDER = 'data'

repos_filename = DATA_FOLDER + '/popular_repos.txt'
languages_in_repos_filename = DATA_FOLDER + '/languages_in_repos.yaml'

with open(languages_in_repos_filename, 'r') as lang_file:
    languages_by_repo = yaml.safe_load(lang_file)


# count lines in file
with open(repos_filename) as f:
    for total, l in enumerate(f):
        pass
total += 1


try:
    with open(repos_filename) as repos_file:
        for repo_id in tqdm(repos_file, total=total):
            repo_id = repo_id.strip('\n')
            if repo_id in languages_by_repo:
                continue
            owner, repo = repo_id.split('/')
            languages_dict = get_repo_languages(owner, repo)
            if languages_dict is not None:
                languages_by_repo[repo_id] = languages_dict
finally:
    with open(languages_in_repos_filename, 'w') as lang_file:
        yaml.dump(languages_by_repo, lang_file, sort_keys=True)
