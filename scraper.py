#!/usr/bin/env python
# encoding: utf-8

# ---------------------------------------------------------------------------------------------------------------------
# Name: scraper.py
# Version: 0.0.1
# Summary: Zap Imoveis Scraper
#
# Author: Alexsander Lopes Camargos
# Author-email: alcamargos@vivaldi.net
#
# License: MIT
# ---------------------------------------------------------------------------------------------------------------------

"""Zap Imoveis Scraper"""

from random import randint

import pandas as pd
import urllib3
from bs4 import BeautifulSoup
from slugify import slugify

CIDADES = ['Belo Horizonte']
# CIDADES = ['Belo Horizonte', 'Contagem', 'Betim', 'Governador Valadares', 'Montes Claros']
TIPOS_IMOVEIS = ['Casas', 'Apartamentos', 'Quitinetes']
BASE_URL = 'www.zapimoveis.com.br'
PORT = 443
CERT_REQS = 'CERT_NONE'


class DataScraper:

    def __init__(self, *args):
        super(DataScraper, self).__init__(*args)

    def __data_to_csv(self):
        http = urllib3.PoolManager()

        valor = []
        tipo_alugel = []
        iptu = []
        area = []
        quartos = []
        banheiros = []
        vagas = []
        uri = []
        cidade = []
        endreco = []
        tipo_negociacao = []

        for _cidade in CIDADES:
            for tipo_imovel in TIPOS_IMOVEIS:
                for page in range(1, 50):
                    sleep_time = randint(60, 120)
                    http = urllib3.HTTPSConnectionPool(BASE_URL, PORT, CERT_REQS)

                    url = '/aluguel/' + slugify(tipo_imovel) + '/mg+' + slugify(
                        _cidade) + '/?pagina=1&tipoUnidade=Residencial,Apartamento&transacao=Aluguel' + str(
                        page)
                    page = http.request('GET', url)

                    soup = BeautifulSoup(page.data.decode('utf-8'), 'html.parser')
                    result = soup.find_all('div', {'class': 'card-container'})

                    for row in result:
                        tipo_negociacao.append(tipo_imovel)
                        cidade.append(_cidade)

                        endereco_find = row.find('h2', 'simple-card__address color-dark text-regular')
                        endereco_text = ''

                        if endereco_find:
                            endereco_text = endereco_find.text

                        endreco.append(endereco_text)

                        valor_find = row.find("p",
                                              "simple-card__price js-price color-darker heading-regular heading-regular__bolder align-left")
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

                        area.append(area_text)

                        quatros_find = row.find_all('li', 'feature__item text-small js-bedrooms')
                        quartos_text = 0

                        for li in quatros_find:
                            quatros_find_span = li.find_all('span')[1]
                            quartos_text = quatros_find_span.text
                            quartos_text = quartos_text.replace(' ', '')

                        quartos.append(quartos_text)

                        vagas_find = row.find_all('li', 'feature__item text-small js-parking-spaces')

                        vagas_text = 0

                        for li in vagas_find:
                            vagas_find_span = li.find_all('span')[1]
                            vagas_text = vagas_find_span.text
                            vagas_text = vagas_text.replace(' ', '')

                        vagas.append(vagas_text)

                        banheiros_find = row.find_all('li', 'feature__item text-small js-bathrooms')

                        banheiros_text = 0

                        for li in banheiros_find:
                            banheiros_text_span = li.find_all('span')[1]
                            banheiros_text = banheiros_text_span.text
                            banheiros_text = banheiros_text.replace(' ', '')

                        banheiros.append(banheiros_text)

        data_frame = pd.DataFrame(valor, columns=['Valor'])
        data_frame['Area'] = area
        data_frame['Quartos'] = quartos
        data_frame['Banheiros'] = banheiros
        data_frame['Vagas'] = vagas
        data_frame['TipoNegociacao'] = tipo_negociacao
        data_frame['TipoAluguel'] = tipo_alugel
        data_frame['Iptu'] = iptu
        data_frame['Cidade'] = cidade
        data_frame['Endereco'] = endreco

        # End scrapper
        data_frame.to_csv('data.csv', index=False)

    def execute(self):
        self.__data_to_csv()


if __name__ == "__main__":
    data = DataScraper()
    data.execute()
