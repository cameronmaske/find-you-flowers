import re
import requests
import xmltodict
from bs4 import BeautifulSoup
import pprint

from db import update_or_create

pp = pprint.PrettyPrinter(indent=4)


def extract_price(string):
    """
    Extracts a float from a string
    u'$44.99' -> 44.99
    """
    return float(re.findall("\d+.\d+", string)[0])


def strip_tags(html):
    soup = BeautifulSoup(html)
    return soup.get_text().encode('utf-8')


def scrap_arena_flowers_xml():
    """
    Scrap Arenaflower's XML sitemap.
    """
    url = 'http://www.arenaflowers.com/all_products/flowers.xml'
    r = requests.get(url)
    # Turn the XML into any easy to handle python dictonary.
    flowers = xmltodict.parse(r.content, dict_constructor=dict)['products']['product']
    for data in flowers:
        flower_data = {
            'name': data['fullname'].encode('utf-8'),
            'url': data['url'],
            'image_url': data['catalog_image_url'],
            'price': extract_price(data['standard_price']),
            'description': BeautifulSoup(data['long_description']).p.get_text().encode('utf-8'),
            'supplier': 'ArenaFlowers',
        }
        print "Found {name}".format(**flower_data)
        update_or_create(flower_data)


def scrap_arena_flowers_sitemap():
    """
    Scrap Arenaflower HTML sitemap.
    """
    url = 'http://www.arenaflowers.com/sitemap'
    r = requests.get(url)
    # Turn the HTML into soup to parse it easily.
    soup = BeautifulSoup(r.content)
    # Can only get flower links.
    flowers_links = soup.find('ul', attrs={'class': 'plain'}).find_all('a', href=re.compile('/flowers/'))
    for link in flowers_links:
        url = "http://www.arenaflowers.com{}".format(link['href'])
        scrap_arena_flower_individual(url)


def scrap_arena_flower_individual(url):
    r = requests.get(url)
    # Turn the HTML into soup to parse it easily.
    soup = BeautifulSoup(r.content)
    try:
        flower_data = {
            'name': soup.find('div', attrs={'id': 'product_name_price'}).find('h1').get_text().encode('utf-8'),
            'url': url,
            'image_url': soup.find('img', attrs={'class': 'daddy_product_image', 'id': '0'})['src'],
            'price': extract_price(soup.find('span', attrs={'class': 'standard_price'}).get_text()),
            'description': soup.find('div', attrs={'id': 'product_copy'}).p.find('p').get_text().encode('utf-8'),
            'supplier': 'ArenaFlowers'
        }
        print "Found {name}".format(**flower_data)
        update_or_create(flower_data)
    except Exception as e:
        print "Failed scrap '{}' - {}".format(url, e)


def scrap_clare_florist_individual(data):
    r = requests.get(data['url'])
    # Turn the HTML into soup to parse it easily.
    soup = BeautifulSoup(r.content)
    try:
        data['description'] = soup.find('span', itemprop='description').get_text().encode('utf-8')
        data['image_url'] = soup.find('img', itemprop='image')['src']
        print "Found {name}".format(**data)
        update_or_create(data)
    except Exception as e:
        print "Failed scrap '{}' - {}".format(data['url'], e)


def scrap_clare_florist():
    """
    Scrap Clare Florist's various price pages.
    """
    urls = [
        'http://www.clareflorist.co.uk/flowers-by-price/35/',
        'http://www.clareflorist.co.uk/flowers-by-price/45/',
        'http://www.clareflorist.co.uk/flowers-by-price/70/',
        'http://www.clareflorist.co.uk/flowers-by-price/100/',
    ]
    # Loop thru each price page.
    for url in urls:
        r = requests.get(url)
        # Parse the HTML using soup.
        soup = BeautifulSoup(r.content)
        # Get the each <div> containing flower details.
        products_divs = soup.find_all('div', attrs={'class': 'product'})
        for product in products_divs:
            data = {
                'name': product.find('div', attrs={'class': 'description'}).get_text().encode('utf-8'),
                'url': product.find('div', attrs={'class': 'description'}).a['href'],
                'price': re.findall("\d+.\d+", product.find('div', attrs={'class': 'price'}).strong.get_text())[0],
                'supplier': 'ClareFlorist'
            }
            try:
                scrap_clare_florist_individual(data)
            except Exception as e:
                print "Failed scrap '{}' - {}".format(data['url'], e)



