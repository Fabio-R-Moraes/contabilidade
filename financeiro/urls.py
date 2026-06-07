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
]
