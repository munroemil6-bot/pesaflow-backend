"""
Accounts URLs

Owner: Mason
Responsibility: Route URLs to authentication views

URL patterns to implement:
# TODO: path('register/', views.register)
# TODO: path('login/', views.login)
# TODO: path('refresh/', views.refresh_token)
# TODO: path('profile/', views.profile)
# TODO: path('logout/', views.logout)
# TODO: path('change-password/', views.change_password)
"""

from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("refresh/", views.RefreshTokenView.as_view(), name="refresh"),
    path("profile/", views.profile, name="profile"),
    path("logout/", views.logout, name="logout"),
    path("change-password/", views.change_password, name="change-password"),
]
