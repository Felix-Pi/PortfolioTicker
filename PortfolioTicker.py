#!/usr/bin/env python3

# <bitbar.title>PortfolioTicker</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>Felix Pieschka</bitbar.author>
# <bitbar.author.github>Felix-Pi</bitbar.author.github>
# <bitbar.desc>Overview for yahoo finance api assets</bitbar.desc>
# <bitbar.image>http://www.hosted-somewhere/pluginimage</bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>
# <bitbar.abouturl>http://url-to-about.com/</bitbar.abouturl>

import requests

from data import assets, db_watchlist

GREEN = '\u001b[32;1m'
RED = '\033[31m'
RESET = '\033[0m'
FONT = "| font='Menlo'"


def get_longest_title_len(db):
    longest = 0
    for elem in db:
        if len(elem['title']) > longest:
            longest = len(elem['title'])
    return longest


def get_format(db):
    length = get_longest_title_len(db) + 3

    return '{:<' + str(length) + '} {:<10} {:<7} {}'


def format_number(number, useColor=False):
    number = round(number, 3)
    prefix = ''
    suffix = ''

    if number > 0:
        prefix += '+'

        # if number < 10:
        # prefix += '0'

        if useColor:
            color = GREEN
    else:
        # if -10 < number < 0:
        # number = str(number)[1:]
        # prefix = '-0'

        if useColor:
            color = RED

    result = prefix + str(number)

    if len(result.split('.')[1]) == 1:
        suffix = '0' + suffix

    if useColor:
        return color + result + suffix + RESET

    return result + suffix


def get_stock_data(stock_list):
    api = 'https://query1.finance.yahoo.com/v7/finance/quote?'

    symbols = [symbol['symbol'] for symbol in stock_list]
    symbols = 'symbols=' + ','.join(symbols)

    # print(api + symbols)

    req = requests.get(api + symbols)
    return req.json()['quoteResponse']['result']


def prepare_asset_db(asset_db):
    data = get_stock_data(asset_db)

    assert len(asset_db) == len(data)

    for i in range(len(asset_db)):
        asset_db[i]['price'] = data[i]['regularMarketPrice']
        asset_db[i]['priceOpen'] = data[i]['regularMarketOpen']

        amount = float(asset_db[i]['amount'])
        buyin = float(asset_db[i]['buyin'])
        price = float(asset_db[i]['price'])
        priceOpen = float(asset_db[i]['priceOpen'])

        value = float(round(amount * price, 2))
        asset_db[i]['value'] = value

        asset_db[i]['profit'] = float(round(value - (amount * buyin), 2))
        asset_db[i]['change_today_euro'] = float(round(value - (amount * priceOpen), 2))

    return asset_db


def prepare_asset(asset):
    asset['db'] = prepare_asset_db(asset['db'])

    asset['profit'] = round(sum(item['profit'] for item in asset['db']), 2)
    asset['value'] = round(sum(item['value'] for item in asset['db']), 2)
    asset['change_today_euro'] = round(sum(item['change_today_euro'] for item in asset['db']), 2)

    return asset


def print_assets(asset):
    asset_db = asset['db']
    asset_value = asset['value']
    asset_profit = asset['profit']

    asset_db = sorted(asset_db, key=lambda entry: entry['value'], reverse=True)

    print(assets_format.format(asset['title'], format_number(asset_value), format_number(asset_profit), FONT))

    out = get_format(asset_db)

    print('--' + out.format('Change Today:', '', format_number(asset['change_today_euro'], True), FONT))
    print('--' + out.format('Change Total:', '', format_number(asset['profit'], True), FONT))
    print('-----')

    for asset in asset_db:
        profit = float(asset['profit'])

        print('--' + out.format(asset['title'], format_number(asset['value']), format_number(profit, True), FONT))


def print_watchlist(asset):
    prepare_asset(asset)
    asset_db = asset['db']

    asset_db = sorted(asset_db, key=lambda entry: entry['value'], reverse=True)

    print(asset['title'] + FONT)

    out = get_format(asset_db)

    for asset in asset_db:
        print('--' + out.format(asset['title'], '', asset['value'], FONT))


if __name__ == '__main__':
    for asset in assets:
        prepare_asset(asset)

    total_profit = round(sum(item['profit'] for item in assets), 2)
    total_value = round(sum(item['value'] for item in assets), 2)

    out = '{} {}'
    print(out.format(format_number(total_profit), FONT))

    print('---')

    assets_format = get_format(assets)

    assets = sorted(assets, key=lambda entry: entry['value'], reverse=True)

    for asset in assets:
        print_assets(asset)

    print('-----')
    print('---')
    print(assets_format.format('Total', format_number(total_value), format_number(total_profit, True), FONT))
    print('---')
    print_watchlist({'title': 'Watchlist', 'db': db_watchlist})
