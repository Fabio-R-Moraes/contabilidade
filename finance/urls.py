from django.urls import path
from . import views

urlpatterns = [
    # Contas
    path('', views.ContaListView.as_view(), name="conta-list"),
    path('constas/nova/', views.contaCreateView.as_view(), name="conta-detail"),
    path('contas/<int:pk>/', views.contaDetailView.as_view(), name="conta-detail"),
    path('contas/<int:pk>/editar/', views.contaUpdateView.as_view(), name="conta-update"),
    path('contas/<int:pk>/excluir/', views.contaDeleteView.as_view(), name="conta-delete"),
    # Operações Globais
    path('operacoes/', views.operacaoListView.as_view(), name="operacao-list"),
    path('operacoes/nova/', views.operacaoCreateView.as_view(), name="operacao-create"),
    path('operacoes/<int:pk>/editar/', views.operacaoUpdateView.as_view(), name="operacao-update"),
    path('operacoes/<int:pk>/excluir/', views.operacaoDeleteView.as_view(), name="operacao-delete"),
    # Operações dentro de uma conta - Atalho
    path(
        'contas/<int:conta_pk>/operacoes/nova/',
        views.operacaoCreateView.as_view(),
        name="operacao-create-para-conta",
    )
]

