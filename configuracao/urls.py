from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reservas/', include('reservas.urls')),

    
    path('', include('reservas.urls')),
]
