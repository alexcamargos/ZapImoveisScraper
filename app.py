#!/usr/bin/env python
# encoding: utf-8

# ---------------------------------------------------------------------------------------------------------------------
# Name: app.py
# Version: 0.0.1
# Summary: Zap Imóveis Scraper
#          A scraper that gathers data from Zap Imóveis website using BeautifulSoup.
#
# Author: Alexsander Lopes Camargos
# Author-email: alcamargos@vivaldi.net
#
# License: MIT
# ---------------------------------------------------------------------------------------------------------------------

from optparse import OptionParser, IndentedHelpFormatter

BANNER = """
'    _____             ___                    _       ____                                 
'   |__  /__ _ _ __   |_ _|_ __ _____   _____(_)___  / ___|  ___ _ __ __ _ _ __   ___ _ __ 
'     / // _` | '_ \   | || '_ ` _ \ \ / / _ | / __| \___ \ / __| '__/ _` | '_ \ / _ | '__|
'    / /| (_| | |_) |  | || | | | | \ V |  __| \__ \  ___) | (__| | | (_| | |_) |  __| |   
'   /____\__,_| .__/  |___|_| |_| |_|\_/ \___|_|___/ |____/ \___|_|  \__,_| .__/ \___|_|   
'             |_|                                                         |_|              
"""


class BannerHelpFormatter(IndentedHelpFormatter):
    """Just a small tweak to optparse to be able to print a banner."""

    def __init__(self, banner, *argv, **argd):
        self.banner = banner
        IndentedHelpFormatter.__init__(self, *argv, **argd)

    def format_usage(self, usage):
        msg = IndentedHelpFormatter.format_usage(self, usage)

        return '%s\n%s' % (self.banner, msg)


# Parse the command line arguments.
FORMATTER_BANNER = BannerHelpFormatter(BANNER +
                                       '\nBy Alexsander Lopes Camargos\n'
                                       'https://github.com/alexcamargos/ZapImoveisScraper\n')

USAGE = "usage: %prog [options] arg"


def main():
    parser = OptionParser(usage=USAGE, formatter=FORMATTER_BANNER)

    parser.add_option('-a',
                      '--address',
                      metavar='ADDRESS',
                      type='string',
                      help='Onde o imóvel está localizado',
                      default='Belo Horizonte')

    parser.add_option('-p',
                      '--pages',
                      metavar='PAGES',
                      type='int',
                      help='Número maximo de páginas a consultar.',
                      default=1)

    parser.add_option('-f',
                      '--filtro',
                      metavar='FILTRO',
                      type='string',
                      help='Ação a ser executada (alugar, comprar ou lançamentos).',
                      default='aluguel')

    parser.add_option('-t',
                      '--tipo',
                      metavar='TIPO',
                      type='string',
                      help='Tipo da unidade alvo da busca (casas, apartamentos, quitinetes, ...).',
                      default='imoveis')

    parser.add_option('-v',
                      '--verbose',
                      metavar='VERBOSE',
                      action="store_true",
                      help='Executar o programa em modo verboso.')

    (options, args) = parser.parse_args()


if __name__ == "__main__":
    main()
