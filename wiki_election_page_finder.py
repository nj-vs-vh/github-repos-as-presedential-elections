import re

import requests

import time

from html.parser import HTMLParser

from tqdm import trange


WIKI_URL = 'https://en.wikipedia.org/'


DATA_FOLDER = './data'

elections_filename = DATA_FOLDER + '/election_wiki_pages.txt'


class WikiElectionRefsParser(HTMLParser):
    elections_regex = re.compile(r'presidential[ _]election', flags=re.IGNORECASE)

    def __init__(self):
        try:
            with open(elections_filename, 'r') as f:
                self.elections = {line.strip('\n') for line in f if line}
        except FileNotFoundError:
            self.elections = set()
        super().__init__()

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        attrs_dict = {k: v for k, v in attrs}
        href = attrs_dict.get('href', '')
        title = attrs_dict.get('title', '')
        if (
            href.startswith('/wiki')
            and (self.elections_regex.search(href) or self.elections_regex.search(title))
            and 'United_States_presidential_election_in_' not in href
            and 'List_of' not in href
        ):
            self.elections.add(href)

    def dump(self):
        with open(elections_filename, 'w') as f:
            for election_ref in sorted(self.elections):
                f.write(election_ref + '\n')


parser = WikiElectionRefsParser()


for year in trange(1900, 2021):
    try:
        start_time = time.time()
        r = requests.get(WIKI_URL + f'wiki/List_of_elections_in_{year}')
        parser.feed(r.text)
        duration = time.time() - start_time
        time.sleep(max(0.5 - duration, 0))
    except Exception as e:
        print(e)
        pass


parser.dump()
