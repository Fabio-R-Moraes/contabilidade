from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'financeiro'

urlpatterns = [
    #Auth
    path('', views.DashboardView.as_view(),name='dashboard'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='financeiro:login'), name='logout'),
    path('registro/', views.RegistroView.as_view(), name='registro'),

    #Contas Credoras
    path('contas/credoras/', views.ContaCredoraListView.as_view(), name='conta_credora_list'),
    path('contas/credoras/nova/', views.ContaCredoraCreateView.as_view(), name='conta_credora_create'),
    path('contas/credoras/<int:pk>/editar/', views.ContaCredoraUpdateView.as_view(), name='conta_credora_update'),
    path('contas/credoras/<int:pk>/excluir/', views.ContaCredoraDeleteView.as_view(), name='conta_credora_delete'),

    #Contas Devedoras
    path('contas/devedoras/', views.ContaDevedoraListView.as_view(), name='conta_devedora_list'),
    path('contas/devedoras/nova/', views.ContaDevedoraCreateView.as_view(), name='conta_devedora_create'),
    path('contas/devedoras/<int:pk>/editar/', views.ContaDevedoraUpdateView.as_view(), name='conta_devedora_update'),
    path('contas/devedoras/<int:pk>/excluir/', views.ContaDevedoraDeleteView.as_view(), name='conta_devedora_delete'),

    #Lancamentos
    path('lancamentos/', views.LancamentoListView.as_view(), name='lancamento_list'),
    path('lancamentos/novo', views.LancamentoCreateView.as_view(), name='lancamento_create'),
    path('lancamentos/<int:pk>/', views.LancamentoDetailView.as_view(), name='lancamento_detail'),
    path('lancamentos/<int:pk>/editar/', views.LancamentoUpdateView.as_view(), name='lancamento_update'),
    path('lancamentos/<int:pk>/excluir/', views.LancamentoDeleteView.as_view(), name='lancamento_delete'),

    #Extrato por Conta
    path('contas/credoras/<int:pk>/extrato/', views.ExtratoContaCredoraView.as_view(), name='extrato_credora'),
    path('contas/devedoras/<int:pk>/extrato/', views.ExtratoContaDevedoraView.as_view(), name='extrato_devedora'),
]
