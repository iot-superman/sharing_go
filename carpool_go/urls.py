from django.contrib import admin
from django.urls import path, include
from rides.views import home
urlpatterns=[path('admin/',admin.site.urls),path('api/',include('rides.urls')),path('',home,name='home')]
