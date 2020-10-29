import re

import requests

from html.parser import HTMLParser

from tqdm import trange


WIKI_URL = 'https://en.wikipedia.org/wiki'

elections_filename = 'election_wiki_pages.txt'


class WikiElectionRefsParser(HTMLParser):
    elections_regex = re.compile(r'presidential[ _]election', flags=re.IGNORECASE)
    year_regex = re.compile(r'\d{4,4}')

    def __init__(self):
        with open(elections_filename, 'r') as f:
            self.elections = {line.strip('\n') for line in f if line}
        super().__init__()

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        attrs_dict = {k: v for k, v in attrs}
        href = attrs_dict.get('href', '')
        title = attrs_dict.get('title', '')
        if self.elections_regex.search(href + title) and self.year_regex.search(href + title):
            self.elections.add(href)

    def dump(self):
        with open(elections_filename, 'w') as f:
            for election_ref in sorted(self.elections):
                f.write(election_ref + '\n')


parser = WikiElectionRefsParser()


for year in trange(1900, 2021):
    r = requests.get(WIKI_URL + f'/List_of_elections_in_{year}')
    try:
        parser.feed(r.text)
    except Exception as e:
        print(e)
        pass


parser.dump()
