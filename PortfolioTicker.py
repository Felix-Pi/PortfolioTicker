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
import json

from data import assets, watchlist

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


def get_format_submenu(title):
    length = len(title) + 5

    return '{:<' + str(length) + '} {:<7} {}'


def format_number(number, useColor=False, addSign=True):
    number = round(number, 2)
    prefix = ''
    suffix = ''

    if number > 0:
        if addSign:
            prefix += '+'

        if useColor:
            color = GREEN
    else:
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
        if 'longName' in data[i]:
            asset_db[i]['name'] = data[i]['longName']
        else:
            asset_db[i]['name'] = data[i]['shortName']

        asset_db[i]['symbol'] = data[i]['symbol']

        amount = float(asset_db[i]['amount'])
        buyin = float(asset_db[i]['buyin'])
        price = float(asset_db[i]['price'])
        priceOpen = float(asset_db[i]['priceOpen'])

        value = float(round(amount * price, 2))
        asset_db[i]['value'] = value

        asset_db[i]['profit'] = float(round(value - (amount * buyin), 2))
        asset_db[i]['change_today_euro'] = float(round(value - (amount * priceOpen), 2))

        # only for stocks
        if 'trailingAnnualDividendRate' in data[i]:
            dividend = float(data[i]['trailingAnnualDividendRate'])
            asset_db[i]['dividendYield'] = float(data[i]['trailingAnnualDividendYield'] * 100)
            asset_db[i]['dividend'] = dividend
            asset_db[i]['myDividend'] = dividend * amount

    return asset_db


def prepare_asset(asset):
    asset['db'] = prepare_asset_db(asset['db'])

    asset['profit'] = round(sum(item['profit'] for item in asset['db']), 2)
    asset['value'] = round(sum(item['value'] for item in asset['db']), 2)
    asset['change_today_euro'] = round(sum(item['change_today_euro'] for item in asset['db']), 2)

    if 'dividend' in asset['db'][0]:
        annualDividends = 0

        for item in asset['db']:
            if 'dividend' in item:
                annualDividends += item['myDividend']

        asset['myDividend'] = round(annualDividends, 2)

    return asset


def print_assets(asset):
    asset_db = asset['db']
    asset_value = asset['value']
    asset_profit = asset['profit']

    asset_db = sorted(asset_db, key=lambda entry: entry['value'], reverse=True)

    print(assets_format.format(asset['title'], format_number(asset_value, False, False), format_number(asset_profit),
                               FONT))

    out = get_format(asset_db)

    print('--' + out.format('Change Today:', '', format_number(asset['change_today_euro'], True), FONT))
    print('--' + out.format('Change Total:', '', format_number(asset['profit'], True), FONT))

    if 'myDividend' in asset:
        print('--' + out.format('Annual Dividends:', '', format_number(asset['myDividend'], False, False), FONT))

    print('-----')
    print('--' + out.format('Title', 'Value', 'Profit', FONT))
    for asset in asset_db:
        profit = float(asset['profit'])

        print(
            '--' + out.format(asset['title'], format_number(asset['value'], False, False), format_number(profit, False),
                              FONT))

        out_sub = get_format_submenu(asset['name'])
        print('----' + out_sub.format(asset['name'], asset['symbol'], FONT))
        print('-------')
        print('----' + out_sub.format('Amount', asset['amount'], FONT))
        print('----' + out_sub.format('Price', asset['price'], FONT))
        print('----' + out_sub.format('Value', format_number(asset['value'], False, False), FONT))
        print('-------')
        print('----' + out_sub.format('Profit', format_number(asset['profit'], True, True), FONT))
        print('----' + out_sub.format('Profit Today', format_number(asset['change_today_euro'], True, True), FONT))

        print('-------')

        if 'dividend' in asset:
            print('----' + out_sub.format('Dividends:', format_number(asset['myDividend'], False, False), FONT))
            print('------' + out_sub.format('Annual Dividends:', format_number(asset['dividend'], False, False), FONT))
            print('------' + out_sub.format('Dividends yield:',
                                            str(format_number(asset['dividendYield'], False, False)) + '%', FONT))
            print('------')
            print('------' + out_sub.format('My Dividends:', format_number(asset['myDividend'], True, False), FONT))


def print_watchlist(asset):
    prepare_asset(asset)
    asset_db = asset['db']

    asset_db = sorted(asset_db, key=lambda entry: entry['value'], reverse=True)

    print(asset['title'] + FONT)

    out = get_format(asset_db)

    for asset in asset_db:
        print('--' + out.format(asset['title'], '', asset['value'], FONT))


def store_assets():
    tmp = sorted(assets[0]['db'], key=lambda entry: entry['value'], reverse=True)

    data = [d['value'] for d in tmp]
    labels = [d['title'] for d in tmp]

    with open('/Users/felixpieschka/dev/python/PortfolioTicker/charts/js/assets_save.js', 'w') as outfile:
        outfile.write('var data = ' + str(data) + '; var labels = ' + str(labels) + ';')


if __name__ == '__main__':
    for asset in assets:
        prepare_asset(asset)

    total_value = round(sum(item['value'] for item in assets), 2)
    total_profit = round(sum(item['profit'] for item in assets), 2)
    total_change_today = round(sum(item['change_today_euro'] for item in assets), 2)

    out = '{} {}'
    print(out.format(format_number(total_profit), FONT))

    print('---')

    assets_format = get_format(assets)
    print(assets_format.format('Title', 'Value', 'Profit', FONT))

    assets = sorted(assets, key=lambda entry: entry['value'], reverse=True)

    for asset in assets:
        print_assets(asset)

    print('-----')
    print('---')
    print(assets_format.format('Today', '', format_number(total_change_today, True), FONT))
    print(assets_format.format('Total', format_number(total_value, False, False), format_number(total_profit, True),
                               FONT))
    print('---')
    print_watchlist(watchlist)

store_assets()
