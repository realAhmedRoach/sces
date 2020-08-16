from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.salam.models import ExchangeUser, Order, Firm


@override_settings(Q_CLUSTER={'sync': True})
class APITestCase(TestCase):

    def setUp(self):
        self.warehouse = Firm.objects.create(symbol='TSW', name='Test Warehouse', type='WRHS')
        firm = Firm.objects.create(symbol='TRD', name='Test Firm', type='WRHS')

        self.user = ExchangeUser.objects.create(username='user', password='secure_the_bag', firm=firm)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # BUY ORDERS
        Order.objects.create(firm=self.user.firm, quantity=500, commodity='CL', contract='Z20', order_type='LMT',
                             side='BUY', price=39)
        Order.objects.create(firm=self.user.firm, quantity=500, commodity='CL', contract='Z20', order_type='LMT',
                             side='BUY', price=40)

        # SELL ORDERS
        Order.objects.create(firm=self.user.firm, quantity=500, commodity='CL', contract='Z20', order_type='LMT',
                             side='SELL', price=40)
        Order.objects.create(firm=self.user.firm, quantity=500, commodity='CL', contract='Z20', order_type='LMT',
                             side='SELL', price=41)

    def test_get_bid_ask(self):
        response = self.client.get('/api/bidask/CLZ20/')
        self.assertEquals(float(response.data[0]['price']), 40.0)
        self.assertEquals(float(response.data[1]['price']), 40.0)

