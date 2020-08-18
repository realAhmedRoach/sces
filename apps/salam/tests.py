from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.salam.models import ExchangeUser, Order, Firm, WarehouseReceipt
from commodity import get_tplus_contract_code


@override_settings(Q_CLUSTER={'name': 'scesapi-test', 'sync': True}, SUSPEND_SIGNALS=True)
class APITestCase(TestCase):

    def setUp(self):
        self.warehouse = Firm.objects.create(symbol='TSW', name='Test Warehouse', type='WRHS')
        firm = Firm.objects.create(symbol='TRD', name='Test Firm', type='TRAD')
        other_firm = Firm.objects.create(symbol='NFR', name='New Firm', type='TRAD')

        self.user = ExchangeUser.objects.create(username='user', firm=firm)
        self.user.set_password('secure_the_bag')
        self.user.save()
        self.client = APIClient()
        self.client.login(username='user', password='secure_the_bag')

        self.contract = get_tplus_contract_code(3)

        # BUY ORDERS
        Order.objects.create(firm=self.user.firm, quantity=500, commodity='CL', contract=self.contract,
                             order_type='LMT',
                             side='BUY', price=39)
        Order.objects.create(firm=self.user.firm, quantity=500, commodity='CL', contract=self.contract,
                             order_type='LMT',
                             side='BUY', price=40)

        # SELL ORDERS
        Order.objects.create(firm=other_firm, quantity=500, commodity='CL', contract=self.contract, order_type='LMT',
                             side='SELL', price=40)
        Order.objects.create(firm=other_firm, quantity=500, commodity='CL', contract=self.contract, order_type='LMT',
                             side='SELL', price=41)

    def test_get_bid_ask(self):
        response = self.client.get(reverse('bidask-list') + f'CL{self.contract}/')
        self.assertEquals(float(response.data[0]['price']), 40.0)
        self.assertEquals(float(response.data[1]['price']), 40.0)

    def test_get_all_orders(self):
        response = self.client.get(reverse('order-list'))
        self.assertEquals(len(response.data), 2)

    def test_warehouse_receipt(self):
        WarehouseReceipt.receipts.create(commodity='CL', quantity=100, firm=self.warehouse, warehouse=self.warehouse)

    def test_match_all_orders(self):
        pass

    def test_get_current_price(self):
        pass
