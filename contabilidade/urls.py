from django.urls import path
from .views import indexView, contas, notas

urlpatterns = [
    path('', indexView.as_view(), name='index'),
    path('contas/', contas, name='contas'),
    path('notas/', notas, name='notas'),
]