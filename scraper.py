#!/usr/bin/env python
# encoding: utf-8

# ---------------------------------------------------------------------------------------------------------------------
# Name: scraper.py
# Version: 0.1.3
# Summary: Zap Imóveis Scraper
#          A scraper that gathers data from Zap Imóveis website using BeautifulSoup.
#
# Author: Alexsander Lopes Camargos
# Author-email: alcamargos@vivaldi.net
#
# License: MIT
# ---------------------------------------------------------------------------------------------------------------------

"""
Zap Imóveis Scraper

A scraper that gathers data from Zap Imóveis website using BeautifulSoup.
"""

import json
import logging
import re
import time
from enum import Enum
from random import randint

import pandas as pd
import urllib3
from bs4 import BeautifulSoup
from slugify import slugify

STATES = ['mg']
# TOWNS = ['Belo Horizonte', 'Uberlândia', 'Contagem', 'Juiz de Fora', 'Betim']
TOWNS = ['Belo Horizonte']

# URL templates to make searches.
DOMAIN_NAME = 'www.zapimoveis.com.br'
PATH = '/%(action)s/%(unit_type)s/%(state)s+%(city)s/?pagina=%(page)s'

PORT = 443
CERT_REQS = 'CERT_NONE'
QUANTITY_TO_FETCH = 2
RANDINT_STARTING = 1
RANDINT_FINAL = 1


class BusinessFilter(Enum):
    """Filters groups enumeration."""

    Comprar = 'Venda'
    Alugar = 'Aluguel'
    Lancamentos = 'Lançamentos'


class UnitType(Enum):
    """Unit type filter enumeration."""

    Todos = 'Imoveis'
    Casas = 'Casas'
    Apartamentos = 'Apartamentos'
    Quitinetes = 'Quitinetes'


class ListedItem:
    """A listed item on zapimoveis.com.br."""

    Price = None
    Condominium_fee = None
    IPTU_fee = None
    Floor_size = None
    Number_bedrooms = None
    Number_bathrooms = None
    Parking_spaces = None
    Address = None
    Neighborhood = None
    City = None
    State = None
    Longitude = None
    Latitude = None
    Title = None
    Description = None
    Link = None
    Publisher = None
    Item_ID = None
    Created = None
    Unit_types = None


class DataScraper:
    """Extracting selected data from the site zapimoveis.com.br and save for analysis."""

    def __init__(self, *args):
        """Initiating an empty DataScraper."""

        super(DataScraper, self).__init__(*args)

    @staticmethod
    def __parser_description(description):
        """Parse text description for remove a html tag"""

        # Remove all html tags.
        description_parsed = re.sub(r'^\s*$', '', description)
        # Remove empty lines.
        description_parsed = re.sub(r'\n\s*\n', '\n', description_parsed, re.MULTILINE)

        return description_parsed

    @staticmethod
    def __fetch_data(action, unit_type, city, page):
        """Fetch data on the zapimoveis.com.br website using selection criteria."""

        # Constructing the query using selection criteria.
        query_path = PATH % ({'action': slugify(action),
                              'unit_type': slugify(unit_type),
                              'state': STATES[0],
                              'city': slugify(city),
                              'page': page})

        pool = urllib3.HTTPSConnectionPool(DOMAIN_NAME, PORT, CERT_REQS)

        # Make a request.
        page = pool.request('GET', query_path)

        logging.info(f'GET >> {pool.host}{query_path}\tSTATUS: {page.status}')

        soup = BeautifulSoup(page.data.decode('utf-8'), 'html.parser')

        page_data = soup.find(
            lambda tag: tag.name == "script" and isinstance(tag.string, str) and tag.string.startswith("window"))

        json_string = page_data.string.replace("window.__INITIAL_STATE__=", "").replace(
            ";(function(){var s;(s=document.currentScript||document.scripts["
            "document.scripts.length-1]).parentNode.removeChild(s);}());",
            "")

        return json.loads(json_string)['results']['listings']

    @staticmethod
    def __data_to_csv(data):
        """Write data to a comma-separated values (csv) file."""

        # Data frame constructor.
        data_frame = pd.DataFrame([(item.Price,
                                    item.Condominium_fee,
                                    item.Floor_size,
                                    item.Number_bedrooms,
                                    item.Number_bathrooms,
                                    item.Parking_spaces,
                                    item.IPTU_fee,
                                    item.Address,
                                    item.Neighborhood,
                                    item.City,
                                    item.State,
                                    item.Longitude,
                                    item.Latitude,
                                    item.Title,
                                    item.Description,
                                    item.Link,
                                    item.Publisher,
                                    item.Item_ID,
                                    item.Created,
                                    item.Unit_types) for item in [item for item in data]],
                                  columns=['Price',
                                           'Condominium',
                                           'FloorSize',
                                           'NumberOfBedrooms',
                                           'NumberOfBathrooms',
                                           'ParkingSpaces',
                                           'IPTU',
                                           'Address',
                                           'Neighborhood',
                                           'City',
                                           'State',
                                           'Longitude',
                                           'Latitude',
                                           'Title',
                                           'Description',
                                           'Link',
                                           'Publisher',
                                           'ItemID',
                                           'Created',
                                           'UnitTypes'])

        # Write data frame to a comma-separated values (csv) file.
        data_frame.to_csv('data.csv', index=False)

    def __data_scraper(self, data):
        """Processing the data obtained from the zapimoveis.com.br website."""

        item = ListedItem()

        item.Price = float(data['listing']['pricingInfos'][0].get('price', 0) if len(
            data['listing']['pricingInfos']) > 0 else 0)
        item.Condominium_fee = float(data['listing']['pricingInfos'][0].get('monthlyCondoFee', 0) if len(
            data['listing']['pricingInfos']) > 0 else 0)
        item.IPTU_fee = float(data['listing']['pricingInfos'][0].get('yearlyIptu', 0) if len(
            data['listing']['pricingInfos']) > 0 else 0)
        item.Floor_size = float(data['listing']['usableAreas'][0] if len(data['listing']['usableAreas']) > 0 else 0)
        item.Number_bedrooms = int(data['listing']['bedrooms'][0] if len(data['listing']['bedrooms']) > 0 else 0)
        item.Number_bathrooms = int(data['listing']['bathrooms'][0] if len(data['listing']['bathrooms']) > 0 else 0)
        item.Parking_spaces = int(
            data['listing']['parkingSpaces'][0] if len(data['listing']['parkingSpaces']) > 0 else 0)
        item.Address = f"{data['link']['data']['street'].strip()}, {data['link']['data']['streetNumber'].strip()}"
        item.Neighborhood = data['link']['data']['neighborhood'].strip()
        item.City = data['link']['data']['city'].strip()
        item.State = data['link']['data']['state'].strip()
        item.Longitude = data['listing']['address']['point']['lat'] if data['listing']['address'].get('point') else None
        item.Latitude = data['listing']['address']['point']['lat'] if data['listing']['address'].get('point') else None
        item.Title = data['listing']['title'].strip()
        item.Description = self.__parser_description(data['listing']['description'].replace('<br>', '\n').strip())
        item.Link = DOMAIN_NAME + data['link']['href']
        item.Publisher = data['account']['name'].strip()
        item.Item_ID = data['listing']['id'].strip()
        item.Created = data['listing']['createdAt'].strip()
        item.Unit_types = data['listing']['unitTypes'][0].strip()

        return item

    def __get_data(self):
        """Processing the pagination of results."""

        listed_items = []

        for query_town in TOWNS:
            for unit_type in UnitType:
                for page in range(1, QUANTITY_TO_FETCH):
                    sleep_time = randint(RANDINT_STARTING, RANDINT_FINAL)

                    results = self.__fetch_data(BusinessFilter.Comprar.value, unit_type.value, query_town, page)

                    for result in results:
                        listed_items.append(self.__data_scraper(result))

                    logging.info(f'Delay execution: {sleep_time}')
                    time.sleep(sleep_time)

        return listed_items

    def execute(self):
        """Write data to a comma-separated values (csv) file."""

        self.__data_to_csv(self.__get_data())


def main():
    """Execute when the module is not initialized from an import statement."""

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    logging.info('Zap Imóveis Scraper --- Started')

    data = DataScraper()
    data.execute()

    logging.info('Zap Imóveis Scraper --- Finished')


if __name__ == "__main__":
    main()
