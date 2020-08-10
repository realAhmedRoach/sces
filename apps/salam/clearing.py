from apps.salam.models import Order, Transaction


def match_order(order: Order):
    if order.filled:
        order.delete()
        return

    contract_code = order.commodity + order.contract
    to_fill = order.quantity_unfilled

    if order.side == 'BUY':
        best_ask: Order = Order.bidask.best_ask(contract_code=contract_code)
        if not best_ask:
            return
        crossed_spread = order.order_type == 'MKT' or order.price >= best_ask.price
        if crossed_spread:
            price = best_ask.price
            quantity = to_fill if to_fill < best_ask.quantity_unfilled else best_ask.quantity_unfilled

            transaction = Transaction(long_firm=order.firm, short_firm=best_ask.firm, price=price, quantity=quantity)
            transaction.save()

            order.quantity_filled += quantity
            best_ask.quantity_filled += quantity

            if best_ask.filled:
                best_ask.delete()
            if order.filled:
                order.delete()
            else:
                match_order(order)
    elif order.side == 'SELL':
        best_bid: Order = Order.bidask.best_bid(contract_code=contract_code)
        if not best_bid:
            return
        crossed_spread = order.order_type == 'MKT' or order.price <= best_bid.price
        if crossed_spread:
            price = best_bid.price
            quantity = to_fill if to_fill < best_bid.quantity_unfilled else best_bid.quantity_unfilled

            transaction = Transaction(long_firm=best_bid.firm, short_firm=order.firm, price=price, quantity=quantity)
            transaction.save()

            order.quantity_filled += quantity
            best_bid.quantity_filled += quantity

            if best_bid.filled:
                best_bid.delete()
            if order.filled:
                order.delete()
            else:
                match_order(order)
