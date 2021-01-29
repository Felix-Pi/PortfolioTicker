#!/usr/bin/env python3

# <bitbar.title>PortfolioTicker</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>Felix Pieschka</bitbar.author>
# <bitbar.author.github>Felix-Pi</bitbar.author.github>
# <bitbar.desc>Short description of what your plugin does.</bitbar.desc>
# <bitbar.image>http://www.hosted-somewhere/pluginimage</bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>
# <bitbar.abouturl>http://url-to-about.com/</bitbar.abouturl>

import requests

from data import portfolio, watchlist

def get_stock_data(stock_list):
    api = 'https://query1.finance.yahoo.com/v7/finance/quote?'

    symbols = [symbol['symbol'] for symbol in stock_list]
    symbols = 'symbols=' + ','.join(symbols)

    req = requests.get(api + symbols)
    return req.json()['quoteResponse']['result']


def parse_stock_data(stock_list):
    data = get_stock_data(stock_list)

    assert len(stock_list) == len(data)

    for i in range(len(stock_list)):
        stock_list[i]['price'] = data[i]['regularMarketPrice']

        if 'amount' in stock_list[i]:
            amount = stock_list[i]['amount']
        else:
            amount = 1

        stock_list[i]['value'] = round(amount * float(stock_list[i]['price']), 2)
        stock_list[i]['change'] = round(data[i]['regularMarketChangePercent'], 2)

        if stock_list[i]['change'] < 0:
            stock_list[i]['change'] = '{}{} %'.format('', stock_list[i]['change'], '')
        else:
            stock_list[i]['change'] = '{}{} % '.format('+', stock_list[i]['change'], 'green')

    return stock_list


def print_performance(title, stock_list, printValue=True):
    data = parse_stock_data(stock_list)
    stock_info = '{:<15} {:<8} {:<10}'

    for stock in stock_list:
        print(stock_info.format(stock['title'], stock['value'], stock['change']))

    if printValue:
        print("---")
        print("Value:", round(sum(item['value'] for item in data), 2))


if __name__ == '__main__':
    print_performance('Portfolio', portfolio)
    print_performance('Watchlist', watchlist, False)
