from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


from .views import (
    CitizenTestView,
    CreateOfficerView,
    MeView,
    RegisterView,
)


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("citizen-test/", CitizenTestView.as_view(), name="citizen_test"),
    path("officers/", CreateOfficerView.as_view(), name="create_officer"),
]
