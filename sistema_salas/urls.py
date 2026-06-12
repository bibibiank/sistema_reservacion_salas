"""
URL configuration for sistema_salas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from reservaciones import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Login, logout, etc.
    path('accounts/', include('django.contrib.auth.urls')),

    # Inicio
    path('', views.lista_reservaciones_view, name='inicio'),

    # Crear reservación
    path(
        'reservar/',
        views.crear_reservacion_view,
        name='crear_reservacion'
    ),

    # Cancelar reservación
    path(
        'cancelar/<int:reservacion_id>/',
        views.cancelar_reservacion_view,
        name='cancelar_reservacion'
    ),
]
