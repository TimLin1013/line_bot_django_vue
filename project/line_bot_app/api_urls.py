from django.urls import path
from . import views

urlpatterns = [
    path('delete_personal/', views.delete_personal, name='delete_personal_api'),
    path('delete_group/', views.delete_group, name='delete_group_api'),
    path('get_personal_account/', views.get_user_account, name='get_user_account_api'),
    path('get_user_account_info/',views.get_user_account_info,name = 'get_user_account_info_api'),
    path('get_keep_temporary/',views.get_keep_temporary,name = 'get_keep_temporary_api'),
    path('get_keep_sure/',views.get_keep_sure,name = 'get_keep_sure_api'),
    path('creategroup/',views.creategroup,name='creategroup_api'),
    path('returncategory/',views.returncategory,name='returncategory_api'),
    path('joingroup/',views.joingroup,name='joingroup_api'),
    path('get_group/',views.get_group,name='get_group_api'),
    path('get_group_account/',views.get_group_account,name='get_group_account_api'),
    path('personal_report/',views.personal_report,name='persoanl_report_api'),
    path('group_report/',views.group_report,name='group_report_api'),
    path('return_group_category/',views.return_group_category,name='return_group_category_api'),
    path('catch_member/',views.catch_member,name='catch_member_api'),
    path('get_payback/',views.get_payback,name='get_payback_api'),
    path('get_group_account_info_classification/',views.get_group_account_info_classificaiton,name = 'get_group_account_info_classification_api'),
    path('get_group_account_info/',views.get_group_account_info,name = 'get_group_account_info_api'),
    path('get_group_keep_temporary/',views.get_group_keep_temporary,name = 'get_group_key_temporary_api'),
    path('get_group_keep_sure/',views.get_group_keep_sure,name = 'get_group_key_sure_api'),
    path('get_personal_expense_data/', views.get_personal_expense_data, name='get_personal_expense_data'),
    path('get_group_expense_data/', views.get_group_expense_data, name='get_group_expense_data'),
    path('mark_as_paid/', views.mark_as_paid, name='mark_as_paid'),

]