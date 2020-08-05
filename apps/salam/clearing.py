from apps.salam.models import Order, Transaction


def create_transaction(long_order: Order, short_order: Order) -> Transaction:
    # TODO: CHECKS: same commodity, different party
    assert long_order.side == 'BUY'
    assert short_order.side == 'SELL'
    first = long_order if long_order.order_time < short_order.order_time else short_order
    # TODO: make sure order doesn't need to be filled in one transaction
    quantity = long_order.quantity if long_order.quantity < short_order.quantity else short_order.quantity
    price = None  # TODO: default to market price
    long_is_market = long_order.order_type == Order.ORDER_TYPES[0][0]
    short_is_market = short_order.order_type == Order.ORDER_TYPES[0][0]
    if long_is_market and short_is_market:
        price = first.price  # TODO: change to market price
    elif long_is_market and not short_is_market:
        price = short_order.price
    elif not long_is_market and short_is_market:
        price = long_order.price
    else:
        assert long_order.price <= short_order.price
        price = first.price
    transaction = Transaction(long_party=long_order.party, short_party=short_order.party,
                              commodity=long_order.commodity, contract=long_order.contract, price=price,
                              quantity=quantity)
    long_order.quantity_filled = quantity
    long_order.save()
    short_order.quantity_filled = quantity
    short_order.save()
    return transaction