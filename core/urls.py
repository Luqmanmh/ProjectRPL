from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('Bookselv.urls')),
    path('admin/', admin.site.urls),
]
