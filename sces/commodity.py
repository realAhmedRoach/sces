import calendar
from enum import Enum
from datetime import datetime

BBL = 'barrel'
BSHL = 'bushel'
OZ = 'troy ounce'
CWT = 'hundredweight'
LB = 'pound'

CONTRACT_MONTHS = [
    ('F', 'Jan'),
    ('G', 'Feb'),
    ('H', 'Mar'),
    ('J', 'Apr'),
    ('K', 'May'),
    ('M', 'Jun'),
    ('N', 'Jul'),
    ('Q', 'Aug'),
    ('U', 'Sep'),
    ('V', 'Oct'),
    ('X', 'Nov'),
    ('Z', 'Dec'),
]


class Commodity(Enum):
    @property
    def name(self):
        return self.value[0]

    @property
    def symbol(self):
        return self.value[1]

    @property
    def long_name(self):
        return self.value[2]

    @property
    def unit(self):
        return self.value[3]

    @property
    def contract_size(self):
        return self.value[4]

    OIL = ('OIL', 'CL', 'Crude Oil', BBL, 1000)

    CORN = ('CORN', 'ZC', 'Corn', BSHL)
    SOYBN = ('SOYBN', 'ZS', 'Soybeans', BSHL)
    SRW = ('SRW', 'ZW', 'SRW Wheat', BSHL)
    HRW = ('HRW', 'KC', 'HRW Wheat', BSHL)

    CPR = ('CPR', 'HG', 'Copper', LB)
    PL = ('PL', 'PL', 'Platinum', OZ)

    # PA = ('PA', 'PA', 'Palladium', OZ)
    # RICE = ('RICE', 'RR', 'Rough Rice', CWT)
    # CFE = ('CFE', 'KC', 'Coffee', LB)
    # RB = ('111659', 'RB', 'RBOB Gasoline')
    # CT = ('033661', 'CT', 'Cotton')
    # LBS = ('058643', 'LBS', 'Random-Length Lumber')
    # ZM = ('SN', 'ZM', 'Soybean Meal')
    # LE = ('057642', 'LE', 'Live Cattle')
    # CC = ('073732', 'CC', 'Cocoa')
    # ZO = ('004603', 'ZO', 'Oats')
    # GF = ('061641', 'GF', 'Feeder Cattle')
    # SB = ('080732', 'SB', 'Sugar')
    # ZL = ('007601', 'ZL', 'Soybean Oil')


def get_energy_commodities():
    return [Commodity.OIL]


def get_agricultural_commodities():
    return [Commodity.CORN, Commodity.SOYBN, Commodity.SRW, Commodity.HRW]


def get_metal_commodities():
    return [Commodity.GLD, Commodity.SI, Commodity.CPR, Commodity.PL]


def get_commodity_choices():
    return [(com.symbol, com.long_name) for com in Commodity]


def get_valid_contracts():
    contracts = []

    month = datetime.now().month
    year = datetime.now().year

    last_trade_day = calendar.monthrange(year, month)[1] - 10
    if datetime.now().day > last_trade_day:
        month += 1

    for y in range(2):
        for m in range(12):
            code = CONTRACT_MONTHS[month - 1][0] + str((year % 1000) + y)
            verbose = CONTRACT_MONTHS[month - 1][1] + ' ' + str(year + y)
            contracts.append((code, verbose))
            month = (month + 1) if month < 12 else 1
            if month == 1:
                year += 1

    return contracts
