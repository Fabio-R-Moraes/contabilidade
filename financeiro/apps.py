from django.apps import AppConfig


class FinanceiroConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'financeiro'
    verbose_name = 'Controle Financeiro Familiar'

    def ready(self):
        import financeiro.signals #noqa: F401 - registra os receivers
