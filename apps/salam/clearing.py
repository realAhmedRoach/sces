from apps.salam.models import Order, Transaction


def get_market_price(contract_code):
    # TODO: Cache market price?
    return Transaction.transactions.current_price(contract_code=contract_code).price


def create_transaction(long_order: Order, short_order: Order, trade_price=None, save=True) -> Transaction:
    assert long_order.side == 'BUY'
    assert short_order.side == 'SELL'
    assert long_order.firm != short_order.firm
    assert long_order.commodity == short_order.commodity
    assert long_order.contract == short_order.contract
    first = long_order if long_order.order_time < short_order.order_time else short_order

    # fill in one transaction
    if long_order.fill_in_one:
        assert short_order.quantity >= long_order.quantity
    if short_order.fill_in_one:
        assert long_order.quantity >= short_order.quantity

    # choose lowest quantity
    quantity = long_order.quantity if long_order.quantity < short_order.quantity else short_order.quantity
    price = trade_price if trade_price else get_market_price(long_order.commodity + long_order.contract)
    long_is_market = long_order.order_type == Order.ORDER_TYPES[0][0]
    short_is_market = short_order.order_type == Order.ORDER_TYPES[0][0]
    if (long_is_market and short_is_market) and not price:
        price = first.price  # if there is no market price defaults to first price
    elif long_is_market and not short_is_market:
        if price:
            price = short_order.price if short_order.price > price else price  # get highest price for limit sell
        else:
            price = short_order.price
    elif not long_is_market and short_is_market:
        if price:
            price = long_order.price if long_order.price < price else price  # get lowest price for limit buy
        else:
            price = long_order.price
    else:
        assert long_order.price <= short_order.price  # if they are both limit orders, they both must be in range
        price = first.price
    transaction = Transaction(long_party=long_order.firm, short_party=short_order.firm,
                              commodity=long_order.commodity, contract=long_order.contract, price=price,
                              quantity=quantity)
    if save:
        transaction.save()

    # update quantites
    long_order.quantity_filled = quantity
    long_order.save()
    short_order.quantity_filled = quantity
    short_order.save()

    return transaction