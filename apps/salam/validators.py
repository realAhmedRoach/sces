from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from sces.commodity import get_valid_contracts


def validate_contract_code(value):
    choices = [choice[0] for choice in get_valid_contracts()]
    if value not in choices:
        raise ValidationError(_('This is not a valid contract code. Here are the valid codes: ') + str(choices))