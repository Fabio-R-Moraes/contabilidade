from django.urls import path
from .views import index, contas, notas

urlpatterns = [
    path('', index, name='index'),
    path('contas/', contas, name='contas'),
    path('notas/', notas, name='notas'),
]