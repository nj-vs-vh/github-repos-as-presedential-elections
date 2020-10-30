import re
import yaml
from collections import defaultdict
from tqdm import tqdm

import requests
from bs4 import BeautifulSoup, Tag

from countries_adapter import country_matching_re, get_common_name


WIKI_URL = 'https://en.wikipedia.org'


class ElectionsParsingError(Exception):
    pass


def concat_substrings(tag):
    return (' '.join(s.strip() for s in tag.strings)).strip()


def parse_country_and_year(soup):
    main_div = soup.find(id='mw-content-text')
    country, year = None, None
    for paragraph in main_div.find_all('p'):
        text = concat_substrings(paragraph)
        try:
            if country is None:
                match = next(country_matching_re.finditer(text))
                country = get_common_name(match.group())
        except StopIteration:
            pass
        try:
            if year is None:
                match = next(re.finditer(r'\d{4,4}', text))
                year = match.group()
        except StopIteration:
            pass
        if country and year:
            return country, year
    raise ElectionsParsingError("Unable to parse country or year")


def find_election_results_section(soup):
    for header in soup.find_all(["h2", "h3", "h4"]):
        for tag in header.contents:
            if tag.string == 'Results':
                return header
    raise ElectionsParsingError("Results table not found")


def first_table_under_header(header):
    for tag in header.next_siblings:
        if tag.name == 'table':
            return tag
    raise ElectionsParsingError("Results table not found")


def parse_table_for_election_results(table, headers_log):

    def find_string_idx_in_list_by_ordered_pattern_list(strings, patterns):
        for pattern in patterns:
            for i, string in enumerate(strings):
                if re.match(pattern, string, flags=re.IGNORECASE):
                    return i
        return None

    def parse_vote_count(string):
        try:
            string = string.strip()
            string = string.replace(',', '')
            string = string.strip('%')
            string = string.split('(')[0]
            string = string.split('[')[0]
            return float(string)
        except Exception:
            raise ElectionsParsingError(f"Error while parsing vote count '{string}'")

    tbody = table.find('tbody')
    header_row = tbody.find('tr')

    column_headers = header_row.find_all('th')
    # use colspan attr to determine 'true' column indices
    # each column is repeated as many times as its colspan
    column_headers_plaincolumns = []
    for col in column_headers:
        try:
            repeat = int(col['colspan'])
        except Exception:
            repeat = 1
        for _ in range(repeat):
            column_headers_plaincolumns.append(col)

    column_names = [concat_substrings(th) for th in column_headers_plaincolumns]

    headers_log.write(' | '.join(column_names) + '\n')
    columns_count = len(column_names)

    candidate_patterns = ['presidential candidate', 'candidate', 'electoral values']
    vote_patterns = ['electoral vote', 'vote', r'%', 'public vote', 'total']
    stopword_patterns = [r'.*round']
    candidate_i = find_string_idx_in_list_by_ordered_pattern_list(column_names, candidate_patterns)
    vote_i = find_string_idx_in_list_by_ordered_pattern_list(column_names, vote_patterns)
    if find_string_idx_in_list_by_ordered_pattern_list(column_names, stopword_patterns) is not None:
        raise ElectionsParsingError("Election with first and second round")
    if candidate_i is None or vote_i is None:
        raise ElectionsParsingError(f"Unable to identify candidate or vote column among {column_names}")

    election_results = dict()
    for row in header_row.next_siblings:
        if not isinstance(row, Tag):
            # skip line-break strings
            continue
        if 'th' in {tag.name for tag in row.children}:
            # skip sub-header
            continue
        tds = row.find_all('td')
        if len(tds) < columns_count:
            # to detect and stop parsing on 'Total' row or something alike
            break
        if not concat_substrings(tds[0]):
            # to account for colored badges before first column
            i_shift = 1
        else:
            i_shift = 0

        candidate = concat_substrings(tds[i_shift + candidate_i])
        votes = parse_vote_count(concat_substrings(tds[vote_i]))
        if not candidate:
            raise ElectionsParsingError(f"Error while parsing candidate: {tds[i_shift + candidate_i]}")
        if re.match('total', candidate, flags=re.IGNORECASE):
            break
        election_results[candidate] = votes

    if not election_results:
        raise ElectionsParsingError(f"No rows found: {tbody.prettify()}")
    else:
        total = sum(election_results.values())
        return {cand: votes / total for cand, votes in sorted(election_results.items(), key=lambda item: item[1])}


def parse_and_save_election_page(election_page, output_stream):
    r = requests.get(WIKI_URL + election_page)
    soup = BeautifulSoup(r.text, 'html.parser')

    elections_data = defaultdict(dict)

    try:
        country, year = parse_country_and_year(soup)
        elections_data[election_page]['country'] = country
        elections_data[election_page]['year'] = year
    except ElectionsParsingError:
        pass

    with open('data/wiki_election_pages_parsing_errors.txt', 'a') as f:
        try:
            results_header = find_election_results_section(soup)
            table = first_table_under_header(results_header)
            with open('data/headers_log.txt', 'a') as headers_log:
                elections_data[election_page]['results'] = parse_table_for_election_results(table, headers_log)
            yaml.dump(dict(elections_data), output_stream)
        except ElectionsParsingError as e:
            f.write(f'Error while parsing {WIKI_URL + election_page}:\n\t{str(e)}\n\n')


pages_filename = 'data/election_wiki_pages.txt'

with open(pages_filename) as f:
    for total, l in enumerate(f):
        pass
total += 1

with open(pages_filename, 'r') as pages_file, open('data/election_results.yaml', 'w') as results_file:
    for page in tqdm(pages_file, total=total):
        page = page.strip()
        parse_and_save_election_page(page, results_file)


# sample_election_page = '/wiki/2006_Finnish_presidential_election'

# with open('temp.yaml', 'w') as f:
#     parse_and_save_election_page(sample_election_page, f)
