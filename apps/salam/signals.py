import functools

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task, schedule

from apps.salam.clearing import match_order
from apps.salam.models import Order, Transaction
from sces.commodity import get_delivery_date


def suspendingreceiver(signal, **decorator_kwargs):
    def suspend_wrapper(func):
        @receiver(signal, **decorator_kwargs)
        @functools.wraps(func)
        def fake_receiver(sender, **kwargs):
            if settings.SUSPEND_SIGNALS:
                return
            return func(sender, **kwargs)

        return fake_receiver

    return suspend_wrapper


@suspendingreceiver(post_save, sender=Order)
def send_order_to_engine(sender, instance, **kwargs):
    for order in Order.objects.all():
        if order.filled:
            order.delete()
        else:
            async_task(match_order, order)


@receiver(post_save, sender=Transaction)
def bank_transfer(sender, instance, **kwargs):
    # TODO: transfer money from long_firm to short_firm (T+2 settlement)
    pass


@suspendingreceiver(post_save, sender=Transaction)
def schedule_delivery(sender, instance: Transaction, **kwargs):
    delivery_date = get_delivery_date(instance.contract)[0]  # get first delivery date for simplicity
    schedule('apps.salam.clearing.delivery', instance.uid, next_run=delivery_date)
    pass
