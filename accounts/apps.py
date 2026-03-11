from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'
def ready(self):
    import ConnectX.signals
