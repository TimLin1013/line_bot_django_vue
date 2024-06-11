from django.urls import path
from . import views

urlpatterns = [
    path('get_personal_account/', views.get_user_account, name='get_user_account_api'),
    path('get_user_account_info/',views.get_user_account_info,name = 'get_user_account_info_api'),
    path('get_keep_temporary/',views.get_keep_temporary,name = 'get_keep_temporary_api'),
    path('get_keep_sure/',views.get_keep_sure,name = 'get_keep_sure_api'),
    path('creategroup/',views.creategroup,name='creategroup_api'),
    path('returncategory/',views.returncategory,name='returncategory_api'),
    path('joingroup/',views.joingroup,name='joingroup_api'),
    path('get_group/',views.get_group,name='get_group_api'),
]