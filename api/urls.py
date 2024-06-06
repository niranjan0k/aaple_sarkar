from django.urls import path
from . import views

urlpatterns = [
    path('api/<str:str>', views.login_pg, name='login_pg'),
]
