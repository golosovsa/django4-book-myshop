from celery import shared_task
from django.core.mail import send_mail
from .models import Order


@shared_task
def order_created(order_pk):
    order = Order.objects.get(pk=order_pk)
    subject = f'Order nr. {order.pk}'
    message = \
        f'Dear {order.first_name},\n\n' \
        f'You have successfully placed an order.\n' \
        f'Your order ID is {order.pk}.'
    mail_sent = send_mail(subject, message, 'admin@myshop.ru', [order.email])
    return mail_sent
