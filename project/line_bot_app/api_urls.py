from django.urls import path
from . import views

urlpatterns = [
    path('get_personal_account/', views.get_user_account, name='get_user_account_api'),
    
]