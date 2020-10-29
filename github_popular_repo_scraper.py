"""Scraping GitHub for popular repos by using Search API"""

import requests
import time
from tqdm import trange


GITHUB_HEADER = {'Accept': 'application/vnd.github.v3+json'}

GITHUB_API_URL = 'https://api.github.com/'


GITHUB_REPO_SEARC_API_URL = GITHUB_API_URL + 'search/repositories'

'?q=the&sort=stars&order=desc&per_page=3&page=2'


popular_english_words = ['the', 'of', 'and', 'to', 'a', 'in', 'that']


popular_repos = set()


min_allowed_query_period = 8  # sec, teqnically 6, but let's play safe
per_page = 100  # max allowed by API


for popular_word in popular_english_words:
    for page in trange(1, 1 + (1000 // per_page + 1)):
        start_time = time.time()
        r = requests.get(
            GITHUB_REPO_SEARC_API_URL,
            params={
                'q': popular_word,
                'sort': 'stars',
                'order': 'desc',
                'per_page': per_page,
                'page': page
            },
            headers=GITHUB_HEADER
        )
        try:
            repos = r.json()['items']
            for repo in repos:
                popular_repos.add(repo['owner']['login'] + '/' + repo['name'])
        except Exception:
            pass
        duration = time.time() - start_time
        time.sleep(max(min_allowed_query_period - duration, 0))


with open('popular_repos.txt', 'w') as f:
    f.writelines(line + '\n' for line in popular_repos)
