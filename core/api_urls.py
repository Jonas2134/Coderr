from django.urls import path, include

urlpatterns = [
    path('', include('auth_app.api.urls')),
    path('', include('profile_app.api.urls')),
    path('', include('offers_app.api.urls')),
]
