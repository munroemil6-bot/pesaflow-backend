

from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path("", views.api_index, name="api-index"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("refresh/", views.RefreshTokenView.as_view(), name="refresh"),
    path("profile/", views.profile, name="profile"),
    path("logout/", views.logout, name="logout"),
    path("change-password/", views.change_password, name="change-password"),
]
