import pandas as pd

# TEST_API_KEY = 'mars_test_343343'
# https://www.ams.usda.gov/mnreports/nw_gr901.txt

loaded = False

prices = None

def load_commodity_data():
    global loaded
    if loaded:
        pass

    from urllib.request import urlopen
    import re

    raw_data = urlopen('https://www.ams.usda.gov/mnreports/gx_gr110.txt')

    data = [line.decode('utf-8').strip() for line in raw_data]  # convert bytes to string and strip whitespace
    data = [line for line in data if line]  # remove empty lines

    start = [i for i in data if i.startswith('Grain')][0]
    start = data.index(start)
    prices_list = data[start:start+10]

    # TODO: this is a temporary solution; fix soon
    prices_list.remove('Terminal Elevator Bids')
    prices_list.remove('Processor Bids')

    prices_list = [re.sub(r'\s{2,}', ',', price) for price in prices_list]

    from io import StringIO

    prices_string = StringIO('\n'.join(prices_list))

    global prices
    prices = pd.read_table(prices_string, sep=',')

    prices.iat[3, 0] = 'Terminal Corn'
    prices.iat[4, 0] = 'Terminal Corn'

    prices.iat[5, 0] = 'Processor Corn'
    prices.iat[6, 0] = 'Processor Corn'

    loaded = True


if __name__ == '__main__':
    load_commodity_data()
    print(prices)
