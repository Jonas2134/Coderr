from django.urls import path, include

urlpatterns = [
    path('', include('auth_app.api.urls')),
    path('', include('profile_app.api.urls')),
    path('', include('offers_app.api.urls')),
    path('', include('orders_app.api.urls')),
    path('', include('reviews_app.api.urls')),
]
