"""Algo_Trade URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path
from App import views  

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('live/',views.home,name="home"),
    path('nse_live_data/',views.live_data,name="nse_live_data"),
    path('main_page/',views.main_page,name="main_page"),
    path('',views.nifty_data,name="nifty_data"),
    path('banknifty_data/',views.banknifty_data,name="banknifty_data"),

]