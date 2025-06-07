from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

# Adicionando nomes de namespace para melhor organização (opcional, mas recomendado)
app_name = 'minha_pagina'

urlpatterns = [
    # Rotas existentes
    path('', views.pagina_inicial, name='home'),
    path('', views.pagina_inicial, name='pagina_inicial'), # Mantido por compatibilidade se usado em algum lugar
    path('consumo-agua/', views.consumo_crb, name='consumo_crb'), # Renomeado para clareza
    path('consumo-gas/', views.consumo_gas, name='consumo_gas'), # Renomeado para clareza
    path('consumo-energia/', views.consumo_energia, name='consumo_energia'), # Renomeado para clareza

    path('login/', auth_views.LoginView.as_view(template_name='minha_pagina/login.html'), name='login'),

    # Novas rotas para a API de consumo (AJAX)
    path('api/registros/', views.api_registros_consumo, name='api_registros_consumo'),
    path('api/remover-ultimo/', views.api_remover_ultimo_registro, name='api_remover_ultimo_registro'),
    path('api/limpar-registros/', views.api_limpar_registros, name='api_limpar_registros'),
    path('api/registrar-volume-inicial/', views.api_registrar_volume_inicial, name='api_registrar_volume_inicial'),


    # Rotas rvn
    path('consumo-agua/', views.consumo_rvn, name='consumo_rvn'),
    path('consumo-gas/', views.consumo_gas_rvn, name='consumo_gas_rvn'),
    path('consumo-energia/', views.consumo_energia_rvn, name='consumo_energia_rvn'),



    # Novas rotas para a API de consumo (AJAX) rvn
    path('consumo_rvn/', views.consumo_rvn_view, name='consumo_rvn'),
    path('consumo-gas-rvn/', views.consumo_gas_rvn, name='consumo_gas_rvn'),
    path('consumo-energia-rvn/', views.consumo_energia_rvn_view, name='consumo_energia_rvn'),
    path('api/rvn/registros/', views.api_registros_rvn, name='api_registros_rvn'),
    path('api/rvn/remover_ultimo/', views.remover_ultimo_rvn, name='api_remover_ultimo_rvn'),
    path('api/rvn/limpar/', views.limpar_tudo_rvn, name='api_limpar_rvn'),
    path('api/rvn/volume_inicial/', views.registrar_volume_inicial_rvn, name='api_registrar_volume_inicial_rvn'),

    path('logout/', views.logout_view, name='logout'),
]

