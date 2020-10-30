"""Scraping GitHub for popular repos by using Search API"""
import os

import requests
from requests.auth import HTTPBasicAuth

import time
from tqdm import trange


GITHUB_HEADER = {'Accept': 'application/vnd.github.v3+json'}

GITHUB_API_URL = 'https://api.github.com/'

GITHUB_REPO_SEARC_API_URL = GITHUB_API_URL + 'search/repositories'

github_auth_token = os.environ.get('GITHUB_TOKEN')


DATA_FOLDER = 'data'
popular_repos_filename = DATA_FOLDER + '/popular_repos.txt'

with open(popular_repos_filename, 'r') as f:
    popular_repos = {line.strip('\n') for line in f}


# TODO: IT-related terms like 'framework', 'library', 'package', 'module', 'pipeline'
#       Specific areas like 'machine learning', 'NLP', 'web', 'system'

# query_words = ['the', 'of', 'and', 'to', 'a', 'in', 'that']
# query_words = ['framework', 'library', 'package', 'module', 'pipeline']
query_words = ['machine learning', 'NLP', 'web', 'system', 'multiplatform', 'development', 'code']


min_allowed_query_period = 3  # sec, tecnically as less as 2 is ok with auth, but we play safe
per_page = 100  # max allowed by API


for word in query_words:
    for page in trange(1, 1 + (1000 // per_page + 1)):
        start_time = time.time()
        r = requests.get(
            GITHUB_REPO_SEARC_API_URL,
            params={
                'q': word,
                'sort': 'stars',
                'order': 'desc',
                'per_page': per_page,
                'page': page
            },
            headers=GITHUB_HEADER,
            auth=HTTPBasicAuth('nj-vs-vh', github_auth_token),
        )
        try:
            repos = r.json()['items']
            for repo in repos:
                popular_repos.add(repo['owner']['login'] + '/' + repo['name'])
        except Exception:
            pass
        duration = time.time() - start_time
        time.sleep(max(min_allowed_query_period - duration, 0))


with open(popular_repos_filename, 'w') as f:
    f.writelines(line + '\n' for line in sorted(popular_repos))
