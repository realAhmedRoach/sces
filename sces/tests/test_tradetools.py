import unittest
from ..tradetools import *


class TradeTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.salam_price = get_salam_price(43.75, 0.05, 3)

    def test_get_salam_price(self):
        self.assertEqual(self.salam_price, 43.203125)

    def test_get_rate(self):
        self.assertEqual(get_rate(self.salam_price, 43.75, 3), 0.05)

    def test_get_ajil_rate(self):
        self.assertEqual(get_ajil_rate(11, 10, 3))


if __name__ == '__main__':
    unittest.main()
