from django.urls import path
from . import views

app_name = 'grabsomore'

urlpatterns = [
    path('register/api-token-auth/', views.register, name='register'),
    path('', views.user_login, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('request-password-reset/', views.send_password_reset, name='request_password_reset'),
    path('reset/<str:token>/', views.reset_user_password, name='password_reset_form'),
    path('reset_password/', views.reset_password, name='reset_password'),
]
