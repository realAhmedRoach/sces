from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from sces.commodity import get_commodity_choices


def validate_contract_code(value):
    choices = [choice[0] for choice in get_commodity_choices()]
    if value not in choices:
        raise ValidationError(_('This is not a valid contract code. Here are the valid codes') + choices)