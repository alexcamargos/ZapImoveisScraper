#!/usr/bin/env python
# encoding: utf-8

# ---------------------------------------------------------------------------------------------------------------------
# Name: scraper.py
# Version: 0.0.2
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

import logging
from enum import Enum
from random import randint

import pandas as pd
import urllib3
from bs4 import BeautifulSoup
from slugify import slugify

TOWNS = ['Belo Horizonte']
STATES = ['mg']
# TOWNS = ['Belo Horizonte', 'Contagem', 'Betim', 'Governador Valadares', 'Montes Claros']

# URL templates to make searches.
DOMAIN_NAME = 'www.zapimoveis.com.br'
PATH = '/%(action)s/%(unit_type)s/%(state)s+%(city)s/?pagina=%(page)s'

PORT = 443
CERT_REQS = 'CERT_NONE'
QUANTITY_TO_FETCH = 3


class BusinessFilter(Enum):
    Comprar = 'Venda'
    Alugar = 'Aluguel'
    Lancamentos = 'Lançamentos'


class UnitType(Enum):
    Todos = 'Imoveis'
    Casas = 'Casas'
    Apartamentos = 'Apartamentos'
    Quitinetes = 'Quitinetes'


class DataScraper:

    def __init__(self, *args):
        super(DataScraper, self).__init__(*args)

    @staticmethod
    def get_data(action, unit_type, city, page):
        """Fetch data on the zapimoveis.com.br website using selection criteria.

        Return all DIVs with card-container class.
        """

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
        page_elements = soup.find_all('div', {'class': 'card-container'})

        return page_elements

    def __data_to_csv(self):
        # http = urllib3.PoolManager()

        valor = []
        tipo_alugel = []
        iptu = []
        area = []
        quartos = []
        banheiros = []
        vagas = []
        uri = []
        cidade = []
        logradouro = []
        bairro = []
        tipo_negociacao = []

        for query_cidade in TOWNS:
            for tipo_imovel in UnitType:
                for page in range(1, QUANTITY_TO_FETCH):
                    sleep_time = randint(60, 120)

                    # Get all DIVs with card-container class.
                    result = self.get_data(BusinessFilter.Alugar.value, tipo_imovel.value, query_cidade, page)

                    for row in result:
                        tipo_negociacao.append(tipo_imovel.value)
                        cidade.append(query_cidade)

                        endereco_find = row.find('h2', 'simple-card__address color-dark text-regular')
                        endereco_text = ''

                        if endereco_find:
                            endereco_text = endereco_find.text
                            endereco_text = endereco_text.strip()

                        if ',' in endereco_text:
                            logradouro_tmp, bairro_tmp = endereco_text.split(',')
                            logradouro.append(logradouro_tmp)
                            bairro.append(bairro_tmp)
                        else:
                            logradouro.append(endereco_text)
                            bairro.append('')

                        valor_find = row.find("p",
                                              "simple-card__price js-price color-darker heading-regular "
                                              "heading-regular__bolder align-left")
                        if valor_find:
                            valor_find = valor_find.text.split('\n')
                            valor.append(valor_find[1].replace('.', '').replace(' ', '').replace('R$', ''))
                            tipo_alugel.append(valor_find[2].replace('/', ''))
                        else:
                            valor.append(0)
                            tipo_alugel.append('')

                        iptu_find = row.find('span', 'card-price__value')

                        if iptu_find:
                            iptu.append(iptu_find.text.replace('R$', '').replace('.', ''))
                        else:
                            iptu.append(0)

                        area_find = row.find_all('li', {'class': 'feature__item text-small js-areas'})
                        area_text = 0

                        for li in area_find:
                            area_find_span = li.find_all('span')[1]
                            area_text = area_find_span.text
                            area_text = area_text.replace('m²', '').replace(' ', '')

                        area.append(area_text.strip())

                        quatros_find = row.find_all('li', 'feature__item text-small js-bedrooms')
                        quartos_text = 0

                        for li in quatros_find:
                            quatros_find_span = li.find_all('span')[1]
                            quartos_text = quatros_find_span.text
                            quartos_text = quartos_text.strip()

                        quartos.append(quartos_text)

                        vagas_find = row.find_all('li', 'feature__item text-small js-parking-spaces')

                        vagas_text = 0

                        for li in vagas_find:
                            vagas_find_span = li.find_all('span')[1]
                            vagas_text = vagas_find_span.text
                            vagas_text = vagas_text.strip()

                        vagas.append(vagas_text)

                        banheiros_find = row.find_all('li', 'feature__item text-small js-bathrooms')

                        banheiros_text = 0

                        for li in banheiros_find:
                            banheiros_text_span = li.find_all('span')[1]
                            banheiros_text = banheiros_text_span.text
                            banheiros_text = banheiros_text.strip()

                        banheiros.append(banheiros_text)
        # End scrapper

        # Data frame constructor.
        data_frame = pd.DataFrame(valor, columns=['Valor'])
        data_frame['Area'] = area
        data_frame['Quartos'] = quartos
        data_frame['Banheiros'] = banheiros
        data_frame['Vagas'] = vagas
        data_frame['TipoNegociacao'] = tipo_negociacao
        data_frame['TipoAluguel'] = tipo_alugel
        data_frame['Iptu'] = iptu
        data_frame['Logradouro'] = logradouro
        data_frame['Bairro'] = bairro
        data_frame['Cidade'] = cidade

        # Write data frame to a comma-separated values (csv) file.
        data_frame.to_csv('data.csv', index=False)

    def execute(self):
        self.__data_to_csv()


def main():
    """Execute when the module is not initialized from an import statement."""

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    logging.info('Zap Imóveis Scraper --- Started')

    data = DataScraper()
    data.execute()

    logging.info('Zap Imóveis Scraper --- Finished')


if __name__ == "__main__":
    main()
