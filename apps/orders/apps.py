from django.apps import AppConfig


class OrdersConfig(AppConfig):
    name = 'apps.orders'
    label = 'orders'

    def ready(self):
        import apps.orders.signals
