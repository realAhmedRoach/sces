from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from apps.salam.clearing import match_order
from apps.salam.models import Order


@receiver(post_save, sender=Order)
def send_order_to_engine(sender, instance, **kwargs):
    for order in Order.objects.all():
        if order.filled:
            order.delete()
        else:
            async_task(match_order, order)