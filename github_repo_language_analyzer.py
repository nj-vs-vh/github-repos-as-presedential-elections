import os

import requests
from requests.auth import HTTPBasicAuth

import yaml


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


languages_by_repo = dict()


with open('popular_repos.txt') as repos_file:
    repo_ids = repos_file.readlines()
    for _repo_id in repo_ids:
        repo_id = _repo_id.strip('\n')
        owner, repo = repo_id.split('/')
        languages_dict = get_repo_languages(owner, repo)
        if languages_dict is not None:
            languages_dict[repo_id] = languages_dict


with open('language_repos.yaml', 'w') as lang_file:
    yaml.dump(languages_by_repo, lang_file)
