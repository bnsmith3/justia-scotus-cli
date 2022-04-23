# -*- coding: utf-8 -*-
"""
Script that grabs and stores data from the Justia website:
    https://supreme.justia.com/
"""
from re import sub
from time import sleep
from random import randint
from typing import List, Dict
import click
import requests
from bs4 import BeautifulSoup as bs
from bs4 import element
from pandas import DataFrame

def parse_search_result(result: element.Tag) -> Dict[str, str]:
    """Parse the given Justia search result and return the results in a dict."""
    case = result.find('a', 'case-name').text.strip()
    docket_num = result.find('a', 'case-name')['href'].split('/')[-2]
    date = ' '.join(result.find('span', 'to-small-font').text.strip().split()[1:])
    url = result.find('div', 'color-green').text.strip()
    return {'case': case, 'docket_num': docket_num, 'date': date, 'url': url}

def get_cases_by_year(year: int) -> List[Dict[str, str]]:
    """Get information on the cases in the given year."""
    url = f'https://supreme.justia.com/cases/federal/us/year/{year}.html'
    resp = requests.get(url)
    page_content = bs(resp.content, 'html.parser')
    results = page_content.find_all('div', 'search-result')
    return list(map(parse_search_result, results))

def get_case_opinions(url: str) -> List[Dict[str, str]]:
    """Get the opinions on the page with the given url."""
    resp = requests.get(url)
    page_content = bs(resp.content, 'html.parser')
    links = page_content.find(id='tab-opinion').find_all('li', 'nav-item')

    opinions = []
    for link in links:
        url_suffix = link.find('a')['href']
        opinions.append({'url': f'{url}{url_suffix}', \
                         'title': sub(r'\s\s+', r' ', \
                                      link.find('a').text.strip()), \
                         'opinion': sub(r'\s\s+', r' ', \
                                        page_content.find(id=url_suffix[1:]).text.strip())})
    return opinions

@click.group()
def cli():
    """The Justia SCOTUS CLI."""
    click.echo('The Justia SCOTUS CLI')

@cli.command('cases')
@click.option('--year', type=int, help='The year the cases were decided')
@click.option('-o', '--output_loc', type=click.File('wb'), \
              help='The filename to use when saving the results')
def get_cases(year: int, output_loc: click.File) -> None:
    """Save metadata on the cases in the given year to file."""
    cases = get_cases_by_year(year)
    DataFrame(cases).to_parquet(output_loc)
    click.echo(f'Metadata on {len(cases):,} cases were found and written to disk.')

@cli.command('opinions')
@click.option('--year', type=int, help='The year the opinions were issued')
@click.option('-o', '--output_dir', type=str, \
              help='The directory in which to save the results')
def get_opinions(year: int, output_dir: str) -> None:
    """Save metadata on the opinions in the given year to file."""
    cases = get_cases_by_year(year)
    DataFrame(cases).to_parquet(f'{output_dir}/{year}_cases.parquet')
    click.echo(f'Metadata on {len(cases):,} cases were found and written to disk.')

    ops = []
    for case in cases:
        sleep(randint(0, 5)) # sleep for some period of time
        ops.extend(get_case_opinions(case['url']))

    DataFrame(ops).to_parquet(f'{output_dir}/{year}_opinions.parquet')
    click.echo(f'Metadata on {len(ops):,} opinions were found and written to disk.')

if __name__=="__main__":
    cli()
