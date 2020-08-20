from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.salam.clearing import match_order
from apps.salam.models import ExchangeUser, Order, Firm, WarehouseReceipt, Transaction
from commodity import get_tplus_contract_code


@override_settings(Q_CLUSTER={'name': 'scesapi-test', 'sync': True}, SUSPEND_SIGNALS=True)
class APITestCase(TestCase):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        cls.warehouse = Firm.objects.create(symbol='TSW', name='Test Warehouse', type='WRHS')
        firm = Firm.objects.create(symbol='TRD', name='Test Firm', type='TRAD')
        other_firm = Firm.objects.create(symbol='NFR', name='New Firm', type='TRAD')

        cls.user = ExchangeUser.objects.create(username='user', firm=firm)
        cls.user.set_password('secure_the_bag')
        cls.user.save()

        cls.contract = get_tplus_contract_code(3)

        # BUY ORDERS
        Order.objects.create(firm=firm, quantity=500, commodity='CL', contract=cls.contract,
                             order_type='LMT',
                             side='BUY', price=39)
        Order.objects.create(firm=firm, quantity=500, commodity='CL', contract=cls.contract,
                             order_type='LMT',
                             side='BUY', price=40)

        # SELL ORDERS
        Order.objects.create(firm=other_firm, quantity=500, commodity='CL', contract=cls.contract, order_type='LMT',
                             side='SELL', price=40)
        Order.objects.create(firm=other_firm, quantity=500, commodity='CL', contract=cls.contract, order_type='LMT',
                             side='SELL', price=41)

    def setUp(self):
        self.client.login(username='user', password='secure_the_bag')

    def test_get_bid_ask(self):
        response = self.client.get(reverse('bidask-detail', args=[f'CL{self.contract}']))
        self.assertEquals(float(response.data[0]['price']), 40.0)
        self.assertEquals(float(response.data[1]['price']), 40.0)

    def test_post_order(self):
        data = {
            'commodity': 'CL',
            'contract': self.contract,
            'price': 45.00,
            'side': 'BUY',
            'quantity': 100,
            'order_type': 'LMT',
            'fill_in_one': True,
        }
        response = self.client.post(reverse('order-list'), data=data, format='json')
        self.assertEquals(45.00, float(response.data['price']))
        self.assertEquals(Order.objects.get(uid=response.data['uid']).firm, self.user.firm)

    def test_get_all_orders(self):
        response = self.client.get(reverse('order-list'))
        self.assertEquals(len(response.data), 2)

    def test_warehouse_receipt(self):
        receipt = WarehouseReceipt(commodity='CL', quantity=100, firm=self.warehouse, warehouse=self.warehouse)
        self.assertRaises(ValidationError, receipt.full_clean)

    def test_match_all_orders(self):
        for order in Order.objects.all():
            match_order(order)
        self.assertEquals(1, Transaction.transactions.count())
        self.assertEquals(40.00, Transaction.transactions.latest().price)

    def test_get_current_price(self):
        Transaction.transactions.create(commodity='CL', contract=self.contract, quantity=100, price=41,
                                        short_firm=self.user.firm, long_firm=self.warehouse)
        response = self.client.get(reverse('price-detail', args=[f'CL{self.contract}']))
        self.assertEquals(41, float(response.data['price']))
