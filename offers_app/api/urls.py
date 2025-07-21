from django.urls import path

from .views import OffersGetPostView

urlpatterns = [
    path('offers/', OffersGetPostView.as_view(), name='offers-list-create'),
]
