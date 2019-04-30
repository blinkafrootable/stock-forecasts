
from bs4 import BeautifulSoup
import random, time, operator, requests, os, pickle
from stock import Stock
from exchange import Exchange

import xlsxwriter
import pandas as pd
from collections import OrderedDict

BASE_URL = 'https://walletinvestor.com/stock-forecast?page={PAGE_NUM}&per-page=100'
BASE_EXCHANGE_URL = 'https://quotes.fidelity.com/webxpress/get_quote?QUOTE_TYPE=&SID_VALUE_ID={SYMBOL}'
TOTAL_PAGES_START = 105
PAUSE_MIN = 1
PAUSE_MAX = 3
STOCKS_FILE = 'stocks.p'
OUTPUT_FILE = 'results.html'

stocks = []
old_stocks = []
total_pages = TOTAL_PAGES_START

def main():
    global BASE_URL
    global TOTAL_PAGES_START
    global PAUSE_MIN
    global PAUSE_MAX
    global STOCKS_FILE
    global OUTPUT_FILE
    global stocks
    global old_stocks
    global total_pages

    if stocks_file_empty():
        scrape_stocks()
    else:
        old_stocks = pickle.load(open(STOCKS_FILE, 'rb'))
        stocks_source = ''
        while True:
            stocks_source = str(input('Would you like to refresh stock forecasts [r] or use preloaded (and possibly out of date) forecasts [p]?'))
            if 'r' in stocks_source or 'p' in stocks_source:
                break
            else:
                print('Invalid response. Try again.')
        if 'r' in stocks_source:
            scrape_stocks()
        else:
            stocks = old_stocks

    sorted_by_14d = sorted(stocks, key=operator.attrgetter('forecast14d_value'), reverse=True)
    forecast14d_data = build_data_table(sorted_by_14d, {'Value':'forecast14d_value', 'Name':'name', 'Symbol':'symbol', 'Price':'price'}, [Exchange.NO_INFO, Exchange.OTC])
    forecast14d_table = pd.DataFrame.from_dict(forecast14d_data)
    sorted_by_3m = sorted(stocks, key=operator.attrgetter('forecast3m_value'), reverse=True)
    forecast3m_data = build_data_table(sorted_by_3m, {'Value':'forecast3m_value', 'Name':'name', 'Symbol':'symbol', 'Price':'price'}, [Exchange.NO_INFO, Exchange.OTC])
    forecast3m_table = pd.DataFrame.from_dict(forecast3m_data)
    sorted_by_6m = sorted(stocks, key=operator.attrgetter('forecast6m_value'), reverse=True)
    forecast6m_data = build_data_table(sorted_by_6m, {'Value':'forecast6m_value', 'Name':'name', 'Symbol':'symbol', 'Price':'price'}, [Exchange.NO_INFO, Exchange.OTC])
    forecast6m_table = pd.DataFrame.from_dict(forecast6m_data)
    sorted_by_1y = sorted(stocks, key=operator.attrgetter('forecast1y_value'), reverse=True)
    forecast1y_data = build_data_table(sorted_by_1y, {'Value':'forecast1y_value', 'Name':'name', 'Symbol':'symbol', 'Price':'price'}, [Exchange.NO_INFO, Exchange.OTC])
    forecast1y_table = pd.DataFrame.from_dict(forecast1y_data)
    sorted_by_5y = sorted(stocks, key=operator.attrgetter('forecast1y_value'), reverse=True)
    forecast5y_data = build_data_table(sorted_by_5y, {'Value':'forecast1y_value', 'Name':'name', 'Symbol':'symbol', 'Price':'price'}, [Exchange.NO_INFO])
    forecast5y_table = pd.DataFrame.from_dict(forecast5y_data)
    print('Outputting data to ' + OUTPUT_FILE)

    try:
        with open(OUTPUT_FILE, 'w') as output:
            output.write(build_html_file({'14 Day Forcast':forecast14d_table, '3 Month Forecast':forecast3m_table, '6 Month Forecast':forecast6m_table, '1 Year Forecast':forecast1y_table, '5 Year Forecast':forecast5y_table}))
    except:
        print('Failed to write to ' + OUTPUT_FILE)

def scrape_stocks():
    global BASE_URL
    global STOCKS_FILE
    global stocks
    global total_pages

    print('Scraping stocks')
    get_page_count()

    pages = []

    for i in range(1, total_pages+1):
        pages.append(i)

    while len(pages) > 0:
        rand_index = random.randint(0, len(pages)-1)
        page = pages[rand_index]
        web_page = requests.get(BASE_URL.replace('{PAGE_NUM}', str(page))).text
        soup = BeautifulSoup(web_page, 'html.parser')
        print('Scanning ' + BASE_URL.replace('{PAGE_NUM}', str(page)))

        data_table = soup.find('table', attrs={'class' : 'currency-desktop-table'})
        rows = data_table.find_all('tr')

        for row in rows:
            if row.has_attr('data-key') == False: # if the row is empty, skip
                continue
            cols = row.find_all('td')
            row_num = 0
            name = symbol = price = forecast14d = forecast3m = forecast6m = forecast1y = forecast5y = rating = ''
            for col in cols:
                link = col.find('a')
                if row_num == 0: # rating
                    rating = link.find('span').text.strip()
                elif row_num == 1: # name and symbol
                    full_name = link.text.strip()
                    last_paranth_index = full_name.rfind('(')
                    # print('\tlast index: ' + str(last_paranth_index))
                    name = full_name[0 : last_paranth_index]
                    symbol = full_name[last_paranth_index : len(full_name)]
                elif row_num == 2: # price
                    price = '$' + str(round(float(col.text.strip()), 2))
                elif row_num == 3: # 14 day forecast
                    forecast14d = link.text.strip().replace(' %', '%')
                elif row_num == 4: # 3 month forecast
                    forecast3m = link.text.strip().replace(' %', '%')
                elif row_num == 5: # 6 month forecast
                    forecast6m = link.text.strip().replace(' %', '%')
                elif row_num == 6: # 1 year forecast
                    forecast1y = link.text.strip().replace(' %', '%')
                elif row_num == 7: # 5 year forecast
                    forecast5y = link.text.strip().replace(' %', '%')

                row_num += 1
            stocks.append(Stock(name, symbol, price, forecast14d, forecast3m, forecast6m, forecast1y, forecast5y, rating))
        del pages[rand_index]

        pause()


    get_unknown_exchanges()

    print('Saving data to ' + STOCKS_FILE)
    pickle.dump(stocks, open(STOCKS_FILE, 'wb'))

    print('Scraping successful!')

def get_unknown_exchanges():
    global BASE_EXCHANGE_URL

    print('Getting unknown exchanges')
    i = 0
    for stock in stocks:

        old_exchange = get_exchange_from_old(stock)
        if stock.exchange == Exchange.UNKNOWN and old_exchange != -1 and old_exchange != Exchange.UNKNOWN:
            stock.exchange = old_exchange
            print('Getting exchange for ' + stock.name + ' ' + stock.symbol)
            print(str(stock.exchange))
            continue

        if stock.exchange == Exchange.UNKNOWN or stock.exchange == Exchange.UNKNOWN_EXCHANGE:
            print('Getting exchange for ' + stock.name + ' ' + stock.symbol)
            pause()
            web_page = requests.get(BASE_EXCHANGE_URL.replace('{SYMBOL}', str(stock.symbol[1 : len(stock.symbol)-1])))
            if web_page.status_code != 200:
                stock.exchange = Exchange.NO_INFO
                print(str(stock.exchange))
                i += 1
                continue
            soup = BeautifulSoup(web_page.text, 'html.parser')
            data_list = soup.find_all('td', attrs={'class' : 'SmallData'})
            next_is_exchange = False
            for data in data_list:
                if next_is_exchange:
                    # print('Next is exchange')
                    exchange = data.text.lower().strip()
                    if 'otc' in exchange:
                        stock.exchange = Exchange.OTC
                    elif 'nyse' in exchange:
                        stock.exchange = Exchange.NYSE
                    elif 'nasdaq' in exchange:
                        stock.exchange = Exchange.NASDAQ
                    elif 'american' in exchange:
                        stock.exchange = Exchange.AMERICAN
                    elif 'bats' in exchange:
                        stock.exchange = Exchange.BATS
                    elif 'iex' in exchange:
                        stock.exchange = Exchange.IEX
                    else:
                        stock.exchange = Exchange.UNKNOWN_EXCHANGE
                    break
                if 'Primary Exchange' == data.text.strip():
                    next_is_exchange = True
            if stock.exchange == Exchange.UNKNOWN:
                stock.exchange = Exchange.NO_INFO # if nothing successful, default to NO_INFO
        print(str(stock.exchange))
        if i % 100 == 0 or i == len(stocks) - 1:
            print('Saving data to ' + STOCKS_FILE)
            pickle.dump(stocks, open(STOCKS_FILE, 'wb'))

        i += 1


def get_exchange_from_old(new_stock):
    global stocks

    if len(old_stocks) == 0:
        return -1

    for old_stock in old_stocks:
        if old_stock.symbol == new_stock.symbol:
            return old_stock.exchange
    return -1

def get_page_count():
    global BASE_URL
    global total_pages
    print('Fetching page count')
    while True:
        web_page = requests.get(BASE_URL.replace('{PAGE_NUM}', str(total_pages))).text
        soup = BeautifulSoup(web_page, 'html.parser')
        next_page = soup.find('li', attrs={'class' : 'next'})
        if 'disabled' in next_page.attrs['class']:
            break;
        total_pages += 1
        pause()
    print(str(total_pages) + ' pages found')


def stocks_file_empty():
    global STOCKS_FILE
    return os.stat(STOCKS_FILE).st_size == 0

def pause():
    global PAUSE_MAX
    global PAUSE_MIN
    time.sleep(PAUSE_MIN + random.random()*(PAUSE_MAX-PAUSE_MIN))

def build_html_file(title_table_dict):
    final_html = '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8">\n<title>Results</title>\n<style>\n.column {\nfloat:center;\n}\n.title {\ntext-align:center\n}\n.dataframe {\nmargin:1em auto;\n}\n.header {\nposition:fixed\n;z-index:99;\n}\n</style>\n</head>\n<body>\n'

    final_html += '<div class=header>'
    for title, table in title_table_dict.items():
        final_html += '<a href="#' + title.replace(' ', '-') + '">' + title + '<br></a>\n'
    final_html += '</div>'

    for title, table in title_table_dict.items():
        final_html += '<div class="column" id="' + title.replace(' ', '-') + '">\n'
        final_html += '<h1 class="title">' + title + '</h1>\n'
        final_html += table.to_html()
        final_html += '\n</div\n>'
    final_html += '</body>\n</html>'
    return final_html

def build_data_table(stock_list, heading_attr_dict, exclude_exchanges):
    data_dict = OrderedDict()
    for heading, attr in heading_attr_dict.items():
        attr_list = []
        for stock in stock_list:
            if stock.exchange in exclude_exchanges:
                continue
            else:
                if 'value' in attr: # if the attribute is a value price
                    attr_list.append('$' + str(round(getattr(stock, attr), 2)))
                else:
                    attr_list.append(getattr(stock, attr))
        data_dict[heading] = attr_list
    data_frame = pd.DataFrame.from_dict(data_dict)
    return data_frame

main()
