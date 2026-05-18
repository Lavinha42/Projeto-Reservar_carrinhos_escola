from django.contrib import admin
from django.urls import path, include
from reservas import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reservas/', include('reservas.urls')),

    
    path('', include('reservas.urls')),
    
    path('excluir-reserva/<int:reserva_id>/', views.excluir_reserva, name='excluir_reserva'),
]