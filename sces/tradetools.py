def get_salam_price(futures_price: float, discount_rate: float, duration: int) -> float:
    '''
    Gets the salam price given the discount rate for prepayment and the time till delivery

    :param futures_price: the expected price of the commodity at delivery
    :param discount_rate: the discount rate for prepayment
    :param duration: months till delivery date
    :return: the salam price, the price to be paid spot for future delivery
    '''
    discount_rate = discount_rate * (duration / 12)
    salam_price = futures_price - (futures_price * discount_rate)
    return salam_price


def get_salam_rate(salam_price: float, futures_price: float, duration: int) -> float:
    '''
    Returns the discount rate per annum of a salam sale

    :param salam_price: the price to be paid spot
    :param futures_price: the expected price on delivery date
    :param duration: months till delivery date
    :return: the discount rate for the salam transaction
    '''
    rate = (futures_price - salam_price) / futures_price
    rate *= 12 / duration
    return rate


def get_ajil_rate(deferred_price: float, spot_price: float, duration: int) -> float:
    '''
    Returns the premium rate paid for a deferred payment sale (BBA)
    :param deferred_price: the price to be paid in the future
    :param spot_price: the current price of the commodity
    :param duration: months till delivery date
    :return: the premium rate for the deffered payment transaction
    '''
    rate = (deferred_price - spot_price) / deferred_price
    rate /= 12 / duration
    return rate


if __name__ == '__main__':
    futures_price = 43.75
    salam_price = get_salam_price(futures_price, 0.05, 3)
    print('Salam price: futures_price: 43.75, discount_rate: 0.05, duration: 3 --', salam_price)
    profit = futures_price - salam_price
    print('Profit:', profit, 'per bushel')
    print('1k bushels:', profit * 1000)
    print('1m bushels:', profit * 1000000)

    print('Rate', get_salam_rate(salam_price, futures_price, 3))
    print('\n---\n')
    print('BBA rate:', get_ajil_rate(11, 10, 3))
