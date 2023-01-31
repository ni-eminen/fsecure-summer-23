"""This script finds hyperlinks within a page pointed to by a URL and organizes them by domain."""
import sys
import urllib.request
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


def parse_page_for_links(hostname: str, path: str):
    """
    Parses the web page for hyperlinks inside HTML <a/> tags.
    :param hostname: The hostname for the URL.
    :param path: The path of the URL.
    :return: Returns a set of URLs included on the page.
    """
    url = f'https://{hostname}{path}'
    with urllib.request.urlopen(url) as source:
        soup = BeautifulSoup(source, 'lxml')

        urls = []
        for a_tag in soup.find_all('a'):
            href = a_tag.get('href')
            if href in ('#', 'javascript:void(0)'):
                continue

            urls.append(urljoin(url, href))

    return set(urls)


def parse_url(url: str):
    """
    Returns dictionary with properties of given URL.
    If property is not found, it is an empty string.
    :param url: URL to be parsed for its properties.
    :return: URL parsed to dictionary of its properties.
    """
    parsed_url_ = urlparse(url)
    domains = parsed_url_.netloc.split('.')
    domains = [d for d in domains if 'www' not in d]
    tld = domains[-1]
    domain = '.'.join(parsed_url_.netloc.split('.')[-2:])
    hostname = '.'.join(domains[0:])
    path = parsed_url_.path if parsed_url_.path else '/'
    links = parse_page_for_links(hostname, path)
    link_dict = {'Same host': [], 'Same domain': [], 'Different domain': []}

    for link in links:
        if f'://{hostname}' in link or f'//www.{hostname}' in link:
            link_dict['Same host'].append(link)
        elif domain in link:
            link_dict['Same domain'].append(link)
        else:
            link_dict['Different domain'].append(link)

    return {'properties': {'tld': tld, 'domain': domain, 'hostname': hostname, 'path': path},
            'links': link_dict}


def display_parsed_url(url_properties: dict):
    """
    Given a URL, displays it neatly in output.
    :param url_properties: Dictionary of URL's properties.
    """
    for key in url_properties['properties']:
        print(f'{key.upper(): <20}{url_properties["properties"][key]}')

    for key in url_properties['links']:
        print(f'{key: <20}', end='')
        for ex in url_properties['links'][key]:
            print(f'{ex: <20}')
            print(f'{"": <20}', end='')
        print()

if len(sys.argv) > 1:
    INP = sys.argv[1]
    while INP != '':
        if 'http' not in INP:
            INP = f'http://{INP}'

        try:
            parsed_url = parse_url(INP)
            display_parsed_url(parsed_url)
            break
        except urllib.error.URLError as error:
            print(error)
            INP = input('URL was not valid. Try another one: ')
else:
    parsed_url = \
        parse_url('https://stackoverflow.com/questions/27803503/get-html-using-python-requests')
    display_parsed_url(parsed_url)
